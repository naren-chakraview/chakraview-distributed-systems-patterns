package internal

import (
	"context"
	"sync"
	"time"

	"github.com/google/uuid"
	"go.uber.org/zap"
)

// SpanAttribute represents a span attribute (key-value pair).
type SpanAttribute struct {
	Key   string      `json:"key"`
	Value interface{} `json:"value"`
}

// Span represents a traced operation.
type Span struct {
	ID           string           `json:"id"`
	TraceID      string           `json:"trace_id"`
	Name         string           `json:"name"`
	StartTime    int64            `json:"start_time"`
	EndTime      int64            `json:"end_time"`
	DurationMs   int64            `json:"duration_ms"`
	Status       string           `json:"status"` // success, error, unknown
	Attributes   []SpanAttribute  `json:"attributes"`
	ParentSpanID string           `json:"parent_span_id,omitempty"`
	ChildSpanIDs []string         `json:"child_span_ids"`
	Events       []TraceEvent     `json:"events"`
	Baggage      map[string]string `json:"baggage"`
}

// TraceEvent represents an event within a span.
type TraceEvent struct {
	Name       string    `json:"name"`
	Timestamp  int64     `json:"timestamp"`
	Attributes []SpanAttribute `json:"attributes"`
}

// Trace represents a complete trace (collection of spans).
type Trace struct {
	ID        string            `json:"id"`
	StartTime int64             `json:"start_time"`
	EndTime   int64             `json:"end_time"`
	Spans     []*Span           `json:"spans"`
	Baggage   map[string]string `json:"baggage"`
}

// Metric represents a collected metric.
type Metric struct {
	Name      string      `json:"name"`
	Type      string      `json:"type"` // counter, gauge, histogram
	Timestamp int64       `json:"timestamp"`
	Value     interface{} `json:"value"`
	Attributes []SpanAttribute `json:"attributes"`
}

// TracerConfig holds configuration for the tracer.
type TracerConfig struct {
	MaxTraces        int           `env:"TRACER_MAX_TRACES,default=10000"`
	MaxSpansPerTrace int           `env:"TRACER_MAX_SPANS_PER_TRACE,default=1000"`
	FlushInterval    time.Duration `env:"TRACER_FLUSH_INTERVAL,default=10s"`
	ExportEndpoint   string        `env:"TRACER_EXPORT_ENDPOINT,default=http://localhost:4318"`
}

// Tracer implements distributed tracing for agents.
// Pattern: Observability / Distributed Tracing
// Reference: docs/patterns/observability/distributed-tracing.md
type Tracer struct {
	mu         sync.RWMutex
	traces     map[string]*Trace        // trace_id -> Trace
	spans      map[string]*Span         // span_id -> Span
	metrics    []*Metric
	config     TracerConfig
	logger     *zap.Logger
	spanCount  int64
	traceCount int64
}

// NewTracer creates a new tracer instance.
func NewTracer(cfg TracerConfig, logger *zap.Logger) *Tracer {
	return &Tracer{
		traces:  make(map[string]*Trace),
		spans:   make(map[string]*Span),
		metrics: make([]*Metric, 0),
		config:  cfg,
		logger:  logger,
	}
}

// StartSpan begins a new span.
func (t *Tracer) StartSpan(ctx context.Context, traceID, spanName string, parentSpanID string, baggage map[string]string) (string, error) {
	t.mu.Lock()
	defer t.mu.Unlock()

	spanID := uuid.New().String()
	now := time.Now().Unix()

	span := &Span{
		ID:           spanID,
		TraceID:      traceID,
		Name:         spanName,
		StartTime:    now,
		Status:       "unknown",
		Attributes:   make([]SpanAttribute, 0),
		ParentSpanID: parentSpanID,
		ChildSpanIDs: make([]string, 0),
		Events:       make([]TraceEvent, 0),
		Baggage:      baggage,
	}

	// Ensure trace exists
	if _, exists := t.traces[traceID]; !exists {
		t.traces[traceID] = &Trace{
			ID:        traceID,
			StartTime: now,
			Spans:     make([]*Span, 0),
			Baggage:   baggage,
		}
		t.traceCount++
	}

	t.spans[spanID] = span
	t.spanCount++

	// Link to parent span
	if parentSpanID != "" {
		if parent, exists := t.spans[parentSpanID]; exists {
			parent.ChildSpanIDs = append(parent.ChildSpanIDs, spanID)
		}
	}

	t.logger.Debug("span started", zap.String("trace_id", traceID), zap.String("span_id", spanID), zap.String("span_name", spanName))

	return spanID, nil
}

// EndSpan completes a span.
func (t *Tracer) EndSpan(ctx context.Context, spanID string, status string) error {
	t.mu.Lock()
	defer t.mu.Unlock()

	span, exists := t.spans[spanID]
	if !exists {
		return ErrSpanNotFound
	}

	now := time.Now().Unix()
	span.EndTime = now
	span.DurationMs = (now - span.StartTime) * 1000
	span.Status = status

	// Add span to trace
	trace, exists := t.traces[span.TraceID]
	if exists {
		trace.Spans = append(trace.Spans, span)
		trace.EndTime = now
	}

	t.logger.Debug("span ended", zap.String("span_id", spanID), zap.String("status", status), zap.Int64("duration_ms", span.DurationMs))

	return nil
}

// RecordSpan records a complete span synchronously.
// RPC: RecordSpan(trace_id, span_name, baggage) -> (span_id)
func (t *Tracer) RecordSpan(ctx context.Context, traceID, spanName string, baggage map[string]string) (string, error) {
	spanID, err := t.StartSpan(ctx, traceID, spanName, "", baggage)
	if err != nil {
		return "", err
	}

	// Add default attribute
	t.AddAttribute(spanID, "recorded_at", time.Now().Unix())

	return spanID, nil
}

// AddAttribute adds an attribute to a span.
func (t *Tracer) AddAttribute(spanID, key string, value interface{}) error {
	t.mu.Lock()
	defer t.mu.Unlock()

	span, exists := t.spans[spanID]
	if !exists {
		return ErrSpanNotFound
	}

	span.Attributes = append(span.Attributes, SpanAttribute{Key: key, Value: value})
	return nil
}

// AddEvent records an event within a span.
func (t *Tracer) AddEvent(spanID, eventName string, attributes map[string]interface{}) error {
	t.mu.Lock()
	defer t.mu.Unlock()

	span, exists := t.spans[spanID]
	if !exists {
		return ErrSpanNotFound
	}

	attrs := make([]SpanAttribute, 0, len(attributes))
	for k, v := range attributes {
		attrs = append(attrs, SpanAttribute{Key: k, Value: v})
	}

	span.Events = append(span.Events, TraceEvent{
		Name:       eventName,
		Timestamp:  time.Now().Unix(),
		Attributes: attrs,
	})

	return nil
}

// GetTrace retrieves a complete trace.
// RPC: GetTrace(trace_id) -> (trace: Trace)
func (t *Tracer) GetTrace(ctx context.Context, traceID string) (*Trace, error) {
	t.mu.RLock()
	defer t.mu.RUnlock()

	trace, exists := t.traces[traceID]
	if !exists {
		return nil, ErrTraceNotFound
	}

	return trace, nil
}

// RecordMetric records a metric.
func (t *Tracer) RecordMetric(ctx context.Context, name, metricType string, value interface{}, attributes map[string]interface{}) {
	t.mu.Lock()
	defer t.mu.Unlock()

	attrs := make([]SpanAttribute, 0, len(attributes))
	for k, v := range attributes {
		attrs = append(attrs, SpanAttribute{Key: k, Value: v})
	}

	metric := &Metric{
		Name:       name,
		Type:       metricType,
		Timestamp:  time.Now().Unix(),
		Value:      value,
		Attributes: attrs,
	}

	t.metrics = append(t.metrics, metric)

	// Keep metrics bounded
	if len(t.metrics) > 100000 {
		t.metrics = t.metrics[50000:] // Keep recent half
	}
}

// GetMetrics retrieves collected metrics.
// RPC: GetMetrics() -> (metrics: [Metric])
func (t *Tracer) GetMetrics(ctx context.Context) []*Metric {
	t.mu.RLock()
	defer t.mu.RUnlock()

	result := make([]*Metric, len(t.metrics))
	copy(result, t.metrics)
	return result
}

// GetTraceStatus returns status of traces.
func (t *Tracer) GetTraceStatus(ctx context.Context) map[string]interface{} {
	t.mu.RLock()
	defer t.mu.RUnlock()

	return map[string]interface{}{
		"total_traces":       t.traceCount,
		"active_traces":      len(t.traces),
		"total_spans":        t.spanCount,
		"active_spans":       len(t.spans),
		"total_metrics":      len(t.metrics),
		"timestamp":          time.Now().Unix(),
	}
}

// CleanupOldTraces removes traces older than age.
func (t *Tracer) CleanupOldTraces(ctx context.Context, maxAge time.Duration) {
	t.mu.Lock()
	defer t.mu.Unlock()

	now := time.Now().Unix()
	cutoff := now - int64(maxAge.Seconds())
	deleted := 0

	for traceID, trace := range t.traces {
		if trace.EndTime > 0 && trace.EndTime < cutoff {
			// Remove spans
			for _, span := range trace.Spans {
				delete(t.spans, span.ID)
			}
			delete(t.traces, traceID)
			deleted++
		}
	}

	if deleted > 0 {
		t.logger.Info("cleaned up old traces", zap.Int("deleted", deleted))
	}
}
