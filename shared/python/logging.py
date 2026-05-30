"""Structured logging with distributed tracing and vector clock support.

Patterns:
- Logging Strategies (see docs/patterns/observability/logging-strategies.md)
- Distributed Tracing (see docs/patterns/observability/distributed-tracing.md)

Provides a logger that automatically includes vector clock and trace ID information
in all log entries for better observability in distributed systems.
"""

import json
import logging
from typing import Optional
from shared.python.vector_clock import VectorClock


class StructuredLogger:
    """Structured logger that includes vector clock and trace context.

    All log entries are emitted as JSON with vector clock and trace_id fields
    for better correlation and ordering in distributed tracing systems.
    """

    def __init__(self, name: str):
        """Initialize a StructuredLogger.

        Args:
            name: The logger name (typically the agent ID or module name).
        """
        self.name = name
        self.trace_id: Optional[str] = None
        self.vector_clock: Optional[VectorClock] = None
        self._logger = logging.getLogger(name)

    def set_trace_id(self, trace_id: str) -> None:
        """Set the trace ID for this logger context.

        The trace_id is included in all subsequent log entries
        for cross-service request tracing.

        Args:
            trace_id: A unique identifier for the current request/context.
        """
        self.trace_id = trace_id

    def set_vector_clock(self, vector_clock: VectorClock) -> None:
        """Set the vector clock for this logger context.

        The vector clock is included in all subsequent log entries
        to track causality across distributed agents.

        Args:
            vector_clock: The current VectorClock state.
        """
        self.vector_clock = vector_clock

    def _build_log_entry(self, level: str, message: str, **kwargs) -> str:
        """Build a structured log entry as JSON.

        Args:
            level: Log level (INFO, ERROR, DEBUG, etc.).
            message: The log message.
            **kwargs: Additional fields to include in the JSON.

        Returns:
            A JSON-formatted log entry string.
        """
        entry = {
            "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                name=self.name,
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="",
                args=(),
                exc_info=None
            )),
            "level": level,
            "logger": self.name,
            "message": message,
        }

        if self.trace_id:
            entry["trace_id"] = self.trace_id

        if self.vector_clock:
            entry["vector_clock"] = self.vector_clock.clock

        entry.update(kwargs)
        return json.dumps(entry)

    def info(self, message: str, **kwargs) -> None:
        """Log an info-level message with structured context.

        Args:
            message: The log message.
            **kwargs: Additional fields to include in the JSON.
        """
        log_entry = self._build_log_entry("INFO", message, **kwargs)
        self._logger.info(log_entry)

    def error(self, message: str, **kwargs) -> None:
        """Log an error-level message with structured context.

        Args:
            message: The log message.
            **kwargs: Additional fields to include in the JSON.
        """
        log_entry = self._build_log_entry("ERROR", message, **kwargs)
        self._logger.error(log_entry)

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug-level message with structured context.

        Args:
            message: The log message.
            **kwargs: Additional fields to include in the JSON.
        """
        log_entry = self._build_log_entry("DEBUG", message, **kwargs)
        self._logger.debug(log_entry)
