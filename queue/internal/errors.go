package internal

import "errors"

var (
	// ErrQueueFull occurs when queue capacity is exceeded.
	ErrQueueFull = errors.New("queue is full")

	// ErrEmptyQueue occurs when attempting to dequeue from empty queue.
	ErrEmptyQueue = errors.New("queue is empty")

	// ErrInvalidBatchID occurs when batch ID is not found.
	ErrInvalidBatchID = errors.New("batch ID not found")

	// ErrInvalidEventID occurs when event ID is not found.
	ErrInvalidEventID = errors.New("event ID not found")

	// ErrContextCanceled occurs when context is canceled.
	ErrContextCanceled = errors.New("context canceled")
)
