package internal

import "errors"

var (
	// ErrTraceNotFound occurs when trace ID is not found.
	ErrTraceNotFound = errors.New("trace not found")

	// ErrSpanNotFound occurs when span ID is not found.
	ErrSpanNotFound = errors.New("span not found")

	// ErrInvalidTraceID occurs when trace ID is invalid.
	ErrInvalidTraceID = errors.New("invalid trace ID")

	// ErrInvalidSpanID occurs when span ID is invalid.
	ErrInvalidSpanID = errors.New("invalid span ID")

	// ErrContextCanceled occurs when context is canceled.
	ErrContextCanceled = errors.New("context canceled")
)
