#!/usr/bin/env python3
"""
Demo: Token Budgeting Pattern

Demonstrates how agents budget tokens and gracefully degrade when budget is exhausted.

Pattern: docs/patterns/predictability/token-budgeting.md
Pattern: docs/patterns/predictability/behavior-degradation.md

This demo shows:
1. Normal execution with full token budget
2. Budget tracking across multiple invocations
3. Graceful degradation when budget exhausted
4. Token consumption estimation
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class IntentCategory(Enum):
    """Intent categories."""
    PURCHASE = "purchase"
    SUPPORT = "support"
    INQUIRY = "inquiry"
    OTHER = "other"


@dataclass
class AgentConfig:
    """Agent configuration with token budget."""
    agent_id: str
    token_budget: int
    latency_budget_ms: int = 5000


@dataclass
class IntentDetectionResult:
    """Result with token consumption tracking."""
    intent: str
    confidence: float
    reasoning: str
    tokens_consumed: int
    degraded: bool = False


class IntentDetectionAgent:
    """
    Intent Detection Agent with Token Budgeting.

    Demonstrates:
    - Token estimation from message length
    - Budget enforcement
    - Graceful degradation to keyword matching
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.token_usage: Dict[str, int] = {}
        self.call_count = 0

        # Keyword patterns for degraded mode
        self._intent_patterns = {
            IntentCategory.PURCHASE.value: [
                "buy", "purchase", "want", "need", "order", "price"
            ],
            IntentCategory.SUPPORT.value: [
                "help", "support", "issue", "problem", "broken", "fix"
            ],
            IntentCategory.INQUIRY.value: [
                "what", "when", "where", "how", "tell me", "information"
            ],
        }

    async def execute(self, message: str) -> IntentDetectionResult:
        """
        Execute intent detection with token budgeting.

        PATTERN: Token Budgeting
        Estimates token consumption and enforces budget. If budget exceeded,
        switches to degraded mode (keyword matching).
        """
        self.call_count += 1

        # Token estimation: approximate LLM tokenization
        # Real system would use actual tokenizer
        tokens_estimate = max(1, len(message) // 4)

        # Check budget
        total_tokens_used = sum(self.token_usage.values())
        tokens_remaining = self.config.token_budget - total_tokens_used

        if tokens_remaining < tokens_estimate:
            # PATTERN: Behavior Degradation
            return await self._degrade_to_keyword_matching(
                message, tokens_estimate, total_tokens_used
            )

        # Normal path: full inference
        return await self._execute_full_inference(message, tokens_estimate)

    async def _execute_full_inference(
        self, message: str, tokens_estimate: int
    ) -> IntentDetectionResult:
        """Full inference path with full token budget."""
        # Simulate LLM inference
        intent_scores = self._compute_intent_scores_full(message)
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, confidence = best_intent

        reasoning = (
            f"Full inference: Analyzed message → '{intent_name}' "
            f"({confidence:.0%} confidence). Message: '{message[:50]}...'"
        )

        # Track token usage
        self.token_usage[f"call_{self.call_count}"] = tokens_estimate

        return IntentDetectionResult(
            intent=intent_name,
            confidence=confidence,
            reasoning=reasoning,
            tokens_consumed=tokens_estimate,
            degraded=False,
        )

    async def _degrade_to_keyword_matching(
        self, message: str, tokens_estimate: int, total_tokens_used: int
    ) -> IntentDetectionResult:
        """Degraded mode: keyword matching instead of LLM."""
        # Keyword matching uses far fewer tokens
        degraded_tokens = max(1, len(message) // 20)

        intent_scores = self._compute_intent_scores_degraded(message)
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, confidence = best_intent

        # Reduce confidence in degraded mode
        degraded_confidence = min(0.6, confidence * 0.7)

        reasoning = (
            f"DEGRADED: Budget exhausted ({total_tokens_used + tokens_estimate} / "
            f"{self.config.token_budget}). Using keyword matching. "
            f"Detected '{intent_name}' (confidence {degraded_confidence:.0%}, reduced from {confidence:.0%})"
        )

        # Track degraded token usage
        self.token_usage[f"call_{self.call_count}_degraded"] = degraded_tokens

        return IntentDetectionResult(
            intent=intent_name,
            confidence=degraded_confidence,
            reasoning=reasoning,
            tokens_consumed=degraded_tokens,
            degraded=True,
        )

    def _compute_intent_scores_full(self, message: str) -> Dict[str, float]:
        """Full inference scoring."""
        message_lower = message.lower()
        scores = {}

        for intent, keywords in self._intent_patterns.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            score = 0.5 + (min(matches, 3) * 0.15)  # Cap at 0.95
            scores[intent] = min(score, 0.95)

        # Normalize
        total = sum(scores.values()) or 1
        return {k: v / total for k, v in scores.items()}

    def _compute_intent_scores_degraded(self, message: str) -> Dict[str, float]:
        """Degraded mode scoring (binary keyword matching)."""
        message_lower = message.lower()
        scores = {intent: 0.0 for intent in self._intent_patterns.keys()}

        for intent, keywords in self._intent_patterns.items():
            if any(kw in message_lower for kw in keywords):
                scores[intent] = 1.0

        # Normalize
        total = sum(scores.values()) or 1
        if total == 0:
            scores[IntentCategory.OTHER.value] = 1.0
        else:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def get_token_summary(self) -> Dict:
        """Get token usage summary."""
        total_used = sum(self.token_usage.values())
        return {
            "calls": self.call_count,
            "total_tokens_used": total_used,
            "token_budget": self.config.token_budget,
            "tokens_remaining": max(0, self.config.token_budget - total_used),
            "utilization_percent": (total_used / self.config.token_budget) * 100,
            "call_breakdown": self.token_usage,
        }


async def main():
    """Run token budgeting demo."""
    print("=" * 70)
    print("TOKEN BUDGETING DEMO")
    print("=" * 70)
    print()

    # Create agent with limited budget
    config = AgentConfig(agent_id="intent-edge-1", token_budget=50)
    agent = IntentDetectionAgent(config)

    # Test messages
    test_messages = [
        "I want to buy a new laptop",
        "Can you help me with my account?",
        "What are the specifications?",
        "I need assistance right now",
        "Where can I purchase this product?",
        "Tell me more about this",
    ]

    print(f"Agent: {config.agent_id}")
    print(f"Token Budget: {config.token_budget}")
    print()

    # Execute messages
    for i, message in enumerate(test_messages, 1):
        print(f"--- Message {i} ---")
        print(f"Input: '{message}'")
        print(f"Length: {len(message)} chars")

        result = await agent.execute(message)

        print(f"Intent: {result.intent}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Tokens Used: {result.tokens_consumed}")
        print(f"Mode: {'DEGRADED' if result.degraded else 'NORMAL'}")
        print(f"Reasoning: {result.reasoning}")

        # Show budget status
        summary = agent.get_token_summary()
        print(
            f"Budget Status: {summary['total_tokens_used']}/{summary['token_budget']} "
            f"({summary['utilization_percent']:.0f}%)"
        )
        print()

    # Final summary
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    summary = agent.get_token_summary()
    print(f"Total Calls: {summary['calls']}")
    print(f"Total Tokens Used: {summary['total_tokens_used']}")
    print(f"Token Budget: {summary['token_budget']}")
    print(f"Tokens Remaining: {summary['tokens_remaining']}")
    print(f"Budget Utilization: {summary['utilization_percent']:.1f}%")
    print()

    print("Key Insights:")
    print("1. Tokens estimated from message length")
    print("2. Budget checked before each invocation")
    print("3. When budget exhausted, agent degrades gracefully")
    print("4. Degraded mode uses fewer tokens (1/4 of normal)")
    print("5. Confidence reduced in degraded mode (max 60%)")
    print()

    print("Pattern Documentation:")
    print("- Token Budgeting: docs/patterns/predictability/token-budgeting.md")
    print("- Behavior Degradation: docs/patterns/predictability/behavior-degradation.md")


if __name__ == "__main__":
    asyncio.run(main())
