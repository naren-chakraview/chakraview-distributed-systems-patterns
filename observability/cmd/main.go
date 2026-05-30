package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"chakraview/observability/internal"
	"github.com/sethvargo/go-envconfig"
	"go.uber.org/zap"
	"google.golang.org/grpc"
)

// ObservabilityServiceConfig holds service configuration.
type ObservabilityServiceConfig struct {
	Port       int    `env:"OBSERVABILITY_PORT,default=50052"`
	LogLevel   string `env:"LOG_LEVEL,default=info"`
	TracerCfg  internal.TracerConfig
}

// ObservabilityServer implements the observability gRPC service.
// Pattern: Observability / Distributed Tracing
// Reference: docs/patterns/observability/distributed-tracing.md
type ObservabilityServer struct {
	tracer *internal.Tracer
	logger *zap.Logger
}

// NewObservabilityServer creates a new observability server.
func NewObservabilityServer(tracer *internal.Tracer, logger *zap.Logger) *ObservabilityServer {
	return &ObservabilityServer{
		tracer: tracer,
		logger: logger,
	}
}

// RecordSpan records a span for distributed tracing.
// RPC: RecordSpan(trace_id: string, span_name: string, baggage: map) -> (span_id: string)
func (s *ObservabilityServer) RecordSpan(ctx context.Context, traceID, spanName string, baggage map[string]string) (string, error) {
	spanID, err := s.tracer.RecordSpan(ctx, traceID, spanName, baggage)
	if err != nil {
		s.logger.Error("failed to record span", zap.Error(err), zap.String("trace_id", traceID))
		return "", err
	}

	s.logger.Debug("span recorded", zap.String("trace_id", traceID), zap.String("span_id", spanID), zap.String("span_name", spanName))

	return spanID, nil
}

// StartSpan initiates a new span.
func (s *ObservabilityServer) StartSpan(ctx context.Context, traceID, spanName, parentSpanID string, baggage map[string]string) (string, error) {
	spanID, err := s.tracer.StartSpan(ctx, traceID, spanName, parentSpanID, baggage)
	if err != nil {
		s.logger.Error("failed to start span", zap.Error(err), zap.String("trace_id", traceID))
		return "", err
	}

	return spanID, nil
}

// EndSpan completes a span.
func (s *ObservabilityServer) EndSpan(ctx context.Context, spanID, status string) error {
	err := s.tracer.EndSpan(ctx, spanID, status)
	if err != nil {
		s.logger.Error("failed to end span", zap.Error(err), zap.String("span_id", spanID))
		return err
	}

	return nil
}

// AddSpanAttribute adds an attribute to a span.
func (s *ObservabilityServer) AddSpanAttribute(ctx context.Context, spanID, key string, value interface{}) error {
	err := s.tracer.AddAttribute(spanID, key, value)
	if err != nil {
		s.logger.Error("failed to add span attribute", zap.Error(err), zap.String("span_id", spanID))
		return err
	}

	return nil
}

// AddSpanEvent records an event within a span.
func (s *ObservabilityServer) AddSpanEvent(ctx context.Context, spanID, eventName string, attributes map[string]interface{}) error {
	err := s.tracer.AddEvent(spanID, eventName, attributes)
	if err != nil {
		s.logger.Error("failed to add span event", zap.Error(err), zap.String("span_id", spanID))
		return err
	}

	return nil
}

// GetTrace retrieves a complete trace.
// RPC: GetTrace(trace_id: string) -> (trace: Trace)
func (s *ObservabilityServer) GetTrace(ctx context.Context, traceID string) (*internal.Trace, error) {
	trace, err := s.tracer.GetTrace(ctx, traceID)
	if err != nil {
		s.logger.Error("failed to get trace", zap.Error(err), zap.String("trace_id", traceID))
		return nil, err
	}

	s.logger.Info("trace retrieved", zap.String("trace_id", traceID), zap.Int("span_count", len(trace.Spans)))

	return trace, nil
}

// GetMetrics retrieves collected metrics.
// RPC: GetMetrics() -> (metrics: [Metric])
func (s *ObservabilityServer) GetMetrics(ctx context.Context) []*internal.Metric {
	metrics := s.tracer.GetMetrics(ctx)
	s.logger.Debug("metrics retrieved", zap.Int("count", len(metrics)))
	return metrics
}

// GetTraceStatus returns status of traces.
func (s *ObservabilityServer) GetTraceStatus(ctx context.Context) map[string]interface{} {
	return s.tracer.GetTraceStatus(ctx)
}

// RecordMetric records a metric.
func (s *ObservabilityServer) RecordMetric(ctx context.Context, name, metricType string, value interface{}, attributes map[string]interface{}) {
	s.tracer.RecordMetric(ctx, name, metricType, value, attributes)
	s.logger.Debug("metric recorded", zap.String("name", name), zap.String("type", metricType))
}

// cleanupLoop periodically cleans up old traces.
func (s *ObservabilityServer) cleanupLoop(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.tracer.CleanupOldTraces(ctx, 1*time.Hour)
		}
	}
}

// main runs the Observability Service.
func main() {
	// Load configuration
	var cfg ObservabilityServiceConfig
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

	logger.Info("observability service starting", zap.Int("port", cfg.Port))

	// Create tracer
	tracer := internal.NewTracer(cfg.TracerCfg, logger)

	// Create server
	server := NewObservabilityServer(tracer, logger)

	// Start gRPC server
	listener, err := net.Listen("tcp", fmt.Sprintf(":%d", cfg.Port))
	if err != nil {
		logger.Fatal("failed to listen", zap.Error(err))
	}

	grpcServer := grpc.NewServer()
	// Note: Register server with generated protobuf code in production
	logger.Info("grpc server initialized", zap.String("address", listener.Addr().String()))

	// Start cleanup loop
	ctx, cancel := context.WithCancel(context.Background())
	go server.cleanupLoop(ctx, 5*time.Minute)

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

	logger.Info("observability service stopped")
}
