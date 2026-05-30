"""Abstract base class for distributed agents with token budgeting and causality tracking.

Patterns:
- Token Budgeting (see docs/patterns/predictability/token-budgeting.md)
- Understanding Model Decisions (see docs/patterns/observability/understanding-decisions.md)
- Agent Failure Modes (see docs/foundations/agent-failure-modes.md)

Provides a foundation for implementing agents that track token consumption,
manage vector clocks for causality, and log all decisions with structured context.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from shared.python.logging import StructuredLogger
from shared.python.vector_clock import VectorClock


@dataclass
class AgentConfig:
    """Configuration for an Agent.

    Attributes:
        agent_id: Unique identifier for this agent.
        model: The model name or identifier (e.g., "gpt-4", "claude-3").
        temperature: Sampling temperature for model inference (0.0 to 2.0).
        max_tokens: Maximum tokens per inference call.
        token_budget: Total token budget for this agent's lifetime.
        max_context_tokens: Maximum tokens to retain in context window.
    """

    agent_id: str
    model: str
    temperature: float
    max_tokens: int
    token_budget: int
    max_context_tokens: int


class AgentBase(ABC):
    """Abstract base class for distributed agents with token tracking and causality.

    Provides token budgeting, vector clock management, structured logging,
    and a framework for implementing agent decisions.
    """

    def __init__(self, config: AgentConfig):
        """Initialize an agent with the given configuration.

        Args:
            config: An AgentConfig dataclass with agent settings.
        """
        self.config = config
        self.logger = StructuredLogger(config.agent_id)
        self.vector_clock = VectorClock()
        self.vector_clock.increment(config.agent_id)
        self.tokens_consumed = 0
        self.trace_id: Optional[str] = None

    def set_trace_id(self, trace_id: str) -> None:
        """Set the trace ID for this execution context.

        The trace ID is used to correlate logs and messages across distributed systems.

        Args:
            trace_id: A unique identifier for the current request/context.
        """
        self.trace_id = trace_id
        self.logger.set_trace_id(trace_id)

    def set_vector_clock(self, vector_clock: VectorClock) -> None:
        """Update the agent's vector clock (typically received from a message).

        Merges the incoming vector clock and increments the agent's own timestamp.

        Args:
            vector_clock: A VectorClock from an incoming message.
        """
        self.vector_clock.merge(vector_clock)
        self.vector_clock.increment(self.config.agent_id)

    def execute(self, input_data: Any, trace_id: Optional[str] = None) -> Any:
        """Execute the agent with the given input, tracking tokens and causality.

        This is the main entry point for agent execution. It wraps the actual
        implementation with token budgeting, error logging, and vector clock management.

        Args:
            input_data: The input to process.
            trace_id: Optional trace ID for distributed tracing.

        Returns:
            The result from _execute_impl().

        Raises:
            Exception: If token budget is exceeded or _execute_impl fails.
        """
        if trace_id:
            self.set_trace_id(trace_id)

        self.logger.set_vector_clock(self.vector_clock)

        # Check token budget
        if self.tokens_consumed >= self.config.token_budget:
            self.logger.error(
                "Token budget exceeded",
                tokens_consumed=self.tokens_consumed,
                token_budget=self.config.token_budget,
            )
            raise RuntimeError(
                f"Agent {self.config.agent_id} token budget exceeded: "
                f"{self.tokens_consumed} / {self.config.token_budget}"
            )

        try:
            self.logger.info(
                "Executing agent decision",
                model=self.config.model,
                temperature=self.config.temperature,
            )
            result = self._execute_impl(input_data)
            self.logger.info("Agent execution succeeded", result_type=type(result).__name__)
            return result

        except Exception as e:
            self.logger.error(
                "Agent execution failed",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise

    @abstractmethod
    def _execute_impl(self, input_data: Any) -> Any:
        """Implementation of agent execution logic.

        Subclasses must override this method to implement their specific
        decision-making or processing logic. This method should track
        token consumption by updating self.tokens_consumed.

        Args:
            input_data: The input to process.

        Returns:
            The result of processing the input.
        """
        pass
