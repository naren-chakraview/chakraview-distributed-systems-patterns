package internal

import (
	"context"
	"sync"
	"time"

	"github.com/google/uuid"
	"go.uber.org/zap"
)

// Event represents a single queued event.
type Event struct {
	ID        string            `json:"id"`
	Timestamp int64             `json:"timestamp"`
	Data      map[string]string `json:"data"`
	TraceID   string            `json:"trace_id"`
	Acked     bool              `json:"acked"`
}

// Batch represents a batch of events ready for processing.
type Batch struct {
	ID        string     `json:"id"`
	Events    []*Event   `json:"events"`
	CreatedAt int64      `json:"created_at"`
	Acked     bool       `json:"acked"`
	AckedAt   int64      `json:"acked_at"`
}

// QueueConfig holds configuration for the queue.
type QueueConfig struct {
	MaxSize        int           `env:"QUEUE_MAX_SIZE,default=10000"`
	BatchSize      int           `env:"QUEUE_BATCH_SIZE,default=1000"`
	FlushInterval  time.Duration `env:"QUEUE_FLUSH_INTERVAL,default=5s"`
	MaxBatchCount  int           `env:"QUEUE_MAX_BATCH_COUNT,default=100"`
	AckTimeout     time.Duration `env:"QUEUE_ACK_TIMEOUT,default=30s"`
}

// Queue implements fair queuing with batch support.
// Pattern: Failure Recovery / Idempotency & Replay
// Reference: docs/patterns/failure-recovery/idempotency-and-replay.md
type Queue struct {
	mu              sync.RWMutex
	events          []*Event
	pendingBatches  map[string]*Batch // batch_id -> Batch
	eventToBatch    map[string]string // event_id -> batch_id (for deduplication)
	config          QueueConfig
	logger          *zap.Logger
	eventCountMeter int64
	batchCountMeter int64
}

// NewQueue creates a new queue instance.
func NewQueue(cfg QueueConfig, logger *zap.Logger) *Queue {
	return &Queue{
		events:         make([]*Event, 0, cfg.MaxSize),
		pendingBatches: make(map[string]*Batch),
		eventToBatch:   make(map[string]string),
		config:         cfg,
		logger:         logger,
	}
}

// Enqueue adds an event to the queue.
// Returns batch ID if batch is full and ready to send.
func (q *Queue) Enqueue(ctx context.Context, event *Event) (string, error) {
	q.mu.Lock()
	defer q.mu.Unlock()

	if len(q.events) >= q.config.MaxSize {
		return "", ErrQueueFull
	}

	event.ID = uuid.New().String()
	event.Timestamp = time.Now().Unix()
	q.events = append(q.events, event)
	q.eventCountMeter++

	q.logger.Debug("event enqueued", zap.String("event_id", event.ID), zap.String("trace_id", event.TraceID))

	// Trigger batch creation if threshold reached
	if len(q.events) >= q.config.BatchSize {
		return q.createBatchLocked(), nil
	}

	return "", nil
}

// DequeueBatch creates a batch from current events.
func (q *Queue) DequeueBatch(ctx context.Context) (*Batch, error) {
	q.mu.Lock()
	defer q.mu.Unlock()

	if len(q.events) == 0 {
		return nil, ErrEmptyQueue
	}

	// Check pending batch count
	if len(q.pendingBatches) >= q.config.MaxBatchCount {
		return nil, ErrQueueFull
	}

	return q.createBatchLocked(), nil
}

// createBatchLocked creates a batch without holding external lock.
// Caller must hold mu.
func (q *Queue) createBatchLocked() string {
	batchSize := q.config.BatchSize
	if len(q.events) < batchSize {
		batchSize = len(q.events)
	}

	batch := &Batch{
		ID:        uuid.New().String(),
		Events:    q.events[:batchSize],
		CreatedAt: time.Now().Unix(),
		Acked:     false,
	}

	// Track events in batch
	for _, event := range batch.Events {
		q.eventToBatch[event.ID] = batch.ID
	}

	q.pendingBatches[batch.ID] = batch
	q.events = q.events[batchSize:]
	q.batchCountMeter++

	q.logger.Info("batch created", zap.String("batch_id", batch.ID), zap.Int("event_count", len(batch.Events)))

	return batch.ID
}

// AckBatch marks a batch as acknowledged.
func (q *Queue) AckBatch(ctx context.Context, batchID string) error {
	q.mu.Lock()
	defer q.mu.Unlock()

	batch, exists := q.pendingBatches[batchID]
	if !exists {
		return ErrInvalidBatchID
	}

	batch.Acked = true
	batch.AckedAt = time.Now().Unix()

	// Clean up event-to-batch mappings
	for _, event := range batch.Events {
		delete(q.eventToBatch, event.ID)
	}

	// Remove from pending
	delete(q.pendingBatches, batchID)

	q.logger.Info("batch acknowledged", zap.String("batch_id", batchID), zap.Int("event_count", len(batch.Events)))

	return nil
}

// GetStatus returns current queue status.
func (q *Queue) GetStatus(ctx context.Context) map[string]interface{} {
	q.mu.RLock()
	defer q.mu.RUnlock()

	return map[string]interface{}{
		"queue_size":       len(q.events),
		"max_size":         q.config.MaxSize,
		"pending_batches":  len(q.pendingBatches),
		"total_events":     q.eventCountMeter,
		"total_batches":    q.batchCountMeter,
		"event_to_batch":   len(q.eventToBatch),
		"timestamp":        time.Now().Unix(),
	}
}

// GetBatch retrieves a batch by ID (for debugging).
func (q *Queue) GetBatch(ctx context.Context, batchID string) (*Batch, error) {
	q.mu.RLock()
	defer q.mu.RUnlock()

	batch, exists := q.pendingBatches[batchID]
	if !exists {
		return nil, ErrInvalidBatchID
	}

	return batch, nil
}

// FlushOldBatches removes unacknowledged batches older than timeout.
func (q *Queue) FlushOldBatches(ctx context.Context) error {
	q.mu.Lock()
	defer q.mu.Unlock()

	now := time.Now().Unix()
	timeout := int64(q.config.AckTimeout.Seconds())

	for batchID, batch := range q.pendingBatches {
		if !batch.Acked && (now-batch.CreatedAt) > timeout {
			q.logger.Warn("batch timeout, requeing events",
				zap.String("batch_id", batchID),
				zap.Int64("age_seconds", now-batch.CreatedAt))

			// Re-enqueue events
			q.events = append(q.events, batch.Events...)
			delete(q.pendingBatches, batchID)

			// Clean up mappings
			for _, event := range batch.Events {
				delete(q.eventToBatch, event.ID)
			}
		}
	}

	return nil
}
