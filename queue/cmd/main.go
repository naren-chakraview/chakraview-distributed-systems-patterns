package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"chakraview/queue/internal"
	"github.com/sethvargo/go-envconfig"
	"go.uber.org/zap"
	"google.golang.org/grpc"
)

// QueueServiceConfig holds service configuration.
type QueueServiceConfig struct {
	Port       int           `env:"QUEUE_PORT,default=50051"`
	LogLevel   string        `env:"LOG_LEVEL,default=info"`
	QueueCfg   internal.QueueConfig
}

// QueueServer implements the queue gRPC service.
// Pattern: Failure Recovery / Idempotency & Replay
// Reference: docs/patterns/failure-recovery/idempotency-and-replay.md
type QueueServer struct {
	q      *internal.Queue
	logger *zap.Logger
}

// NewQueueServer creates a new queue server.
func NewQueueServer(q *internal.Queue, logger *zap.Logger) *QueueServer {
	return &QueueServer{
		q:      q,
		logger: logger,
	}
}

// EnqueueEvent adds an event to the queue.
// RPC: EnqueueEvent(event: Event) -> (batch_id: string)
func (s *QueueServer) EnqueueEvent(ctx context.Context, eventData map[string]string, traceID string) (string, error) {
	event := &internal.Event{
		Data:    eventData,
		TraceID: traceID,
	}

	batchID, err := s.q.Enqueue(ctx, event)
	if err != nil {
		s.logger.Error("failed to enqueue event", zap.Error(err), zap.String("trace_id", traceID))
		return "", err
	}

	if batchID != "" {
		s.logger.Info("batch ready", zap.String("batch_id", batchID), zap.String("trace_id", traceID))
	}

	return batchID, nil
}

// DequeueBatch retrieves a batch of events.
// RPC: DequeueBatch() -> (batch: Batch)
func (s *QueueServer) DequeueBatch(ctx context.Context) (*internal.Batch, error) {
	batch, err := s.q.DequeueBatch(ctx)
	if err != nil {
		s.logger.Error("failed to dequeue batch", zap.Error(err))
		return nil, err
	}

	s.logger.Info("batch dequeued", zap.String("batch_id", batch.ID), zap.Int("event_count", len(batch.Events)))

	return batch, nil
}

// AckBatch acknowledges a batch as processed.
// RPC: AckBatch(batch_id: string) -> ()
func (s *QueueServer) AckBatch(ctx context.Context, batchID string) error {
	err := s.q.AckBatch(ctx, batchID)
	if err != nil {
		s.logger.Error("failed to acknowledge batch", zap.Error(err), zap.String("batch_id", batchID))
		return err
	}

	return nil
}

// GetQueueStatus returns current queue status.
// RPC: GetQueueStatus() -> (status: map)
func (s *QueueServer) GetQueueStatus(ctx context.Context) map[string]interface{} {
	return s.q.GetStatus(ctx)
}

// flushLoop periodically flushes old batches.
func (s *QueueServer) flushLoop(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			if err := s.q.FlushOldBatches(ctx); err != nil {
				s.logger.Error("flush error", zap.Error(err))
			}
		}
	}
}

// main runs the Queue Service.
func main() {
	// Load configuration
	var cfg QueueServiceConfig
	if err := envconfig.Process(context.Background(), &cfg); err != nil {
		fmt.Fprintf(os.Stderr, "failed to parse config: %v\n", err)
		os.Exit(1)
	}

	// Setup logger
	var logger *zap.Logger
	var err error
	if cfg.LogLevel == "debug" {
		logger, err = zap.NewDevelopment()
	} else {
		logger, err = zap.NewProduction()
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to create logger: %v\n", err)
		os.Exit(1)
	}
	defer logger.Sync()

	logger.Info("queue service starting", zap.Int("port", cfg.Port))

	// Create queue
	q := internal.NewQueue(cfg.QueueCfg, logger)

	// Create server
	server := NewQueueServer(q, logger)

	// Start gRPC server
	listener, err := net.Listen("tcp", fmt.Sprintf(":%d", cfg.Port))
	if err != nil {
		logger.Fatal("failed to listen", zap.Error(err))
	}

	grpcServer := grpc.NewServer()
	// Note: Register server with generated protobuf code in production
	logger.Info("grpc server initialized", zap.String("address", listener.Addr().String()))

	// Start flush loop
	ctx, cancel := context.WithCancel(context.Background())
	go server.flushLoop(ctx, cfg.QueueCfg.FlushInterval)

	// Handle graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		logger.Info("shutting down gracefully")
		cancel()
		grpcServer.GracefulStop()
	}()

	// Serve
	if err := grpcServer.Serve(listener); err != nil {
		logger.Fatal("grpc server error", zap.Error(err))
	}

	logger.Info("queue service stopped")
}
