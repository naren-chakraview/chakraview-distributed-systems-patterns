"""
Intent Detection Agent with Token Budgeting and Behavior Degradation.

This module demonstrates:
- Token Budgeting (pattern: docs/patterns/predictability/token-budgeting.md)
- Behavior Degradation (pattern: docs/patterns/predictability/behavior-degradation.md)
- Understanding Model Decisions (pattern: docs/patterns/observability/understanding-decisions.md)

The agent detects user intent from input messages and gracefully degrades
to keyword matching when token budget is exhausted.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum
import asyncio


class IntentCategory(Enum):
    """Supported intent categories."""
    PURCHASE = "purchase"
    SUPPORT = "support"
    INQUIRY = "inquiry"
    FEEDBACK = "feedback"
    OTHER = "other"


@dataclass
class AgentConfig:
    """Base configuration for agents."""
    agent_id: str
    token_budget: int = 1000
    latency_budget_ms: int = 5000


@dataclass
class IntentDetectionConfig(AgentConfig):
    """Configuration for Intent Detection Agent."""
    intent_categories: List[str] = field(default_factory=lambda: [
        IntentCategory.PURCHASE.value,
        IntentCategory.SUPPORT.value,
        IntentCategory.INQUIRY.value,
        IntentCategory.FEEDBACK.value,
    ])
    confidence_threshold: float = 0.7
    degradation_mode: bool = False


@dataclass
class VectorClock:
    """Simplified vector clock for causal ordering."""
    agent_id: str
    timestamp: int = 0

    def increment(self):
        """Increment the clock."""
        self.timestamp += 1

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {"agent_id": self.agent_id, "timestamp": self.timestamp}


@dataclass
class IntentDetectionResult:
    """Result of intent detection."""
    intent: str
    confidence: float
    reasoning: str
    tokens_consumed: int
    vector_clock: VectorClock
    degraded: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


class IntentDetectionAgent:
    """
    Intent Detection Agent for edge deployments.

    Detects user intent from input messages with graceful degradation
    when token budget is exhausted. Demonstrates token budgeting and
    behavior degradation patterns.
    """

    def __init__(self, config: IntentDetectionConfig):
        """Initialize the intent detection agent.

        Args:
            config: IntentDetectionConfig with agent settings.
        """
        self.config = config
        self.vector_clock = VectorClock(agent_id=config.agent_id)
        self.token_usage: Dict[str, int] = {}
        self.call_count = 0

        # Keyword patterns for intent matching
        self._intent_patterns = {
            IntentCategory.PURCHASE.value: [
                "buy", "purchase", "want", "need", "order", "checkout",
                "price", "cost", "how much", "product", "laptop", "phone",
                "tablet", "computer", "device"
            ],
            IntentCategory.SUPPORT.value: [
                "help", "support", "issue", "problem", "broken", "error",
                "not working", "fix", "trouble", "complaint", "refund",
                "return", "exchange", "warranty", "broken"
            ],
            IntentCategory.INQUIRY.value: [
                "what", "when", "where", "how", "question", "tell me",
                "information", "about", "know", "available", "details",
                "specs", "features", "compatibility"
            ],
            IntentCategory.FEEDBACK.value: [
                "like", "dislike", "love", "hate", "good", "bad", "great",
                "terrible", "review", "opinion", "suggest", "improve",
                "feedback", "comment", "think"
            ],
        }

    async def execute(self, message: str) -> IntentDetectionResult:
        """
        Execute intent detection on the given message.

        PATTERN: Token Budgeting
        Tracks token usage and enforces budget constraints. Estimates tokens
        as len(message) // 4 to approximate LLM tokenization.

        Args:
            message: User input message to analyze.

        Returns:
            IntentDetectionResult with detected intent, confidence, and metadata.
        """
        self.call_count += 1
        self.vector_clock.increment()

        # PATTERN: Token Budgeting
        # Estimate tokens: approximate LLM tokenization
        tokens_estimate = max(1, len(message) // 4)
        total_tokens_used = sum(self.token_usage.values())

        # Check if we have budget remaining
        if total_tokens_used + tokens_estimate > self.config.token_budget:
            # PATTERN: Behavior Degradation
            # Token budget exceeded; degrade to keyword matching
            return await self._degrade_to_keyword_matching(
                message, tokens_estimate, total_tokens_used
            )

        # Normal execution path with full model
        return await self._execute_impl(message, tokens_estimate)

    async def _execute_impl(
        self,
        message: str,
        tokens_estimate: int
    ) -> IntentDetectionResult:
        """
        Execute full intent detection with model inference.

        PATTERN: Understanding Model Decisions
        Returns confidence scores and reasoning for transparency.

        Args:
            message: User input message.
            tokens_estimate: Estimated token count.

        Returns:
            IntentDetectionResult with full inference details.
        """
        # Simulate model inference with simple heuristics
        intent_scores = self._compute_intent_scores(message)

        # Find best intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name = best_intent[0]
        confidence = best_intent[1]

        # Build reasoning
        reasoning = self._build_reasoning(message, intent_scores)

        # Track token usage
        self.token_usage[f"call_{self.call_count}"] = tokens_estimate

        # Create result
        result = IntentDetectionResult(
            intent=intent_name,
            confidence=confidence,
            reasoning=reasoning,
            tokens_consumed=tokens_estimate,
            vector_clock=VectorClock(
                agent_id=self.config.agent_id,
                timestamp=self.vector_clock.timestamp
            ),
            degraded=False
        )

        return result

    async def _degrade_to_keyword_matching(
        self,
        message: str,
        tokens_estimate: int,
        total_tokens_used: int
    ) -> IntentDetectionResult:
        """
        Degrade to keyword matching when token budget is exhausted.

        PATTERN: Behavior Degradation
        Falls back to simple keyword matching instead of model inference.
        This trades accuracy for budget compliance and predictability.

        Args:
            message: User input message.
            tokens_estimate: Estimated token count.
            total_tokens_used: Total tokens already consumed.

        Returns:
            IntentDetectionResult with degraded (keyword-based) intent.
        """
        # Keyword matching uses minimal tokens
        degraded_tokens = max(1, len(message) // 20)

        intent_scores = self._keyword_match(message)
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name = best_intent[0]
        # Reduce confidence for degraded mode: cap at 0.6
        confidence = min(0.6, best_intent[1] * 0.7)

        reasoning = (
            f"DEGRADED MODE: Token budget exhausted ({total_tokens_used + tokens_estimate} "
            f"/ {self.config.token_budget}). Using keyword matching instead of full inference. "
            f"Detected '{intent_name}' via keywords with reduced confidence."
        )

        # Track degraded token usage (much lower)
        self.token_usage[f"call_{self.call_count}_degraded"] = degraded_tokens

        result = IntentDetectionResult(
            intent=intent_name,
            confidence=confidence,
            reasoning=reasoning,
            tokens_consumed=degraded_tokens,
            vector_clock=VectorClock(
                agent_id=self.config.agent_id,
                timestamp=self.vector_clock.timestamp
            ),
            degraded=True
        )

        return result

    def _compute_intent_scores(self, message: str) -> Dict[str, float]:
        """
        Compute intent scores for the message.

        Uses keyword matching with scoring to estimate intent distribution.

        Args:
            message: User input message.

        Returns:
            Dictionary of intent -> confidence score.
        """
        scores = {intent: 0.0 for intent in self._intent_patterns.keys()}
        message_lower = message.lower()

        # Detect if this is a question (ends with ? or starts with question words)
        is_question = "?" in message or any(
            message_lower.startswith(qw) for qw in ["what", "when", "where", "how", "why"]
        )

        # Count keyword matches per intent
        for intent, keywords in self._intent_patterns.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            if matches > 0:
                score = min(0.99, 0.5 + (matches * 0.2))
                # Boost inquiry intent if question detected
                if is_question and intent == IntentCategory.INQUIRY.value:
                    score = min(0.99, score + 0.3)
                scores[intent] = score
            else:
                scores[intent] = 0.1  # No match, minimal score

        # Find best intent
        best_intent = max(scores.items(), key=lambda x: x[1])
        if best_intent[1] > 0.1:
            # If we found a good match, give it high confidence
            # Clear other scores and set winner to high confidence
            for intent in scores:
                if intent == best_intent[0]:
                    scores[intent] = 0.85
                else:
                    scores[intent] = 0.05
        else:
            # No good match, distribute evenly
            scores = {k: 1.0 / len(scores) for k in scores}

        return scores

    def _keyword_match(self, message: str) -> Dict[str, float]:
        """
        Simple keyword matching for degraded mode.

        Returns boolean indicators (0.0 or 1.0) for each intent.

        Args:
            message: User input message.

        Returns:
            Dictionary of intent -> match indicator (0.0 or 1.0).
        """
        scores = {intent: 0.0 for intent in self._intent_patterns.keys()}
        message_lower = message.lower()

        # Simple keyword matching
        for intent, keywords in self._intent_patterns.items():
            if any(kw in message_lower for kw in keywords):
                scores[intent] = 1.0

        # If no matches, default to "other"
        if not any(scores.values()):
            scores[IntentCategory.OTHER.value] = 1.0
        else:
            # Normalize if multiple matches
            total = sum(scores.values())
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def _build_reasoning(
        self,
        message: str,
        intent_scores: Dict[str, float]
    ) -> str:
        """
        Build a human-readable reasoning explanation.

        PATTERN: Understanding Model Decisions
        Provides transparency into how the agent arrived at its decision.

        Args:
            message: User input message.
            intent_scores: Computed intent scores.

        Returns:
            Reasoning explanation string.
        """
        sorted_intents = sorted(
            intent_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_intent = sorted_intents[0]
        reasoning = (
            f"Intent detected based on message analysis: '{message[:50]}...' "
            f"→ '{top_intent[0]}' (confidence: {top_intent[1]:.1%}). "
            f"Top alternatives: {', '.join([f'{k} ({v:.0%})' for k, v in sorted_intents[1:3]])}"
        )

        return reasoning

    def get_token_usage_summary(self) -> Dict:
        """Get summary of token usage."""
        total_used = sum(self.token_usage.values())
        return {
            "total_calls": self.call_count,
            "total_tokens_used": total_used,
            "token_budget": self.config.token_budget,
            "token_budget_remaining": max(0, self.config.token_budget - total_used),
            "budget_utilization": total_used / self.config.token_budget,
            "call_breakdown": self.token_usage
        }
