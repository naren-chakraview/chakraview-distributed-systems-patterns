"""
Fraud Detection Agent with Risk Scoring and Context Window Management.

This module demonstrates:
- Context Window Management (pattern: docs/patterns/predictability/context-window-management.md)
- Understanding Model Decisions (pattern: docs/patterns/observability/understanding-decisions.md)

The agent detects fraudulent transactions by analyzing transaction context
(user history, velocity, amount) and assigning risk scores that guide
allow/challenge/block decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import asyncio


class RiskAction(Enum):
    """Recommended actions based on fraud risk."""
    ALLOW = "allow"
    CHALLENGE = "challenge"
    BLOCK = "block"


@dataclass
class AgentConfig:
    """Base configuration for agents."""
    agent_id: str
    token_budget: int = 1000
    latency_budget_ms: int = 5000


@dataclass
class FraudDetectionConfig(AgentConfig):
    """Configuration for Fraud Detection Agent."""
    risk_threshold: float = 0.7
    max_transaction_value: int = 10000
    alert_cooldown_minutes: int = 5
    max_recent_transactions: int = 10


@dataclass
class TransactionContext:
    """Context for evaluating a transaction."""
    user_id: str
    recent_transactions: List[Dict] = field(default_factory=list)
    average_transaction_value: float = 0.0
    card_velocity: int = 0  # Transactions per hour


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
class FraudDetectionResult:
    """Result of fraud detection analysis."""
    fraud_risk: float
    recommended_action: str
    reasoning: str
    tokens_consumed: int
    vector_clock: VectorClock
    risk_factors: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class FraudDetectionAgent:
    """
    Fraud Detection Agent for edge deployments.

    Analyzes transaction context and assigns fraud risk scores to guide
    allow/challenge/block decisions. Demonstrates context window management
    and decision transparency.
    """

    def __init__(self, config: FraudDetectionConfig):
        """Initialize the fraud detection agent.

        Args:
            config: FraudDetectionConfig with agent settings.
        """
        self.config = config
        self.vector_clock = VectorClock(agent_id=config.agent_id)
        self.token_usage: Dict[str, int] = {}
        self.call_count = 0
        self.last_alert_time: Dict[str, datetime] = {}

    async def execute(
        self,
        transaction: Dict,
        context: TransactionContext
    ) -> FraudDetectionResult:
        """
        Execute fraud detection on the given transaction.

        PATTERN: Context Window Management
        Limits recent transaction history to max_recent_transactions
        to control context window size and improve efficiency.

        Args:
            transaction: Transaction data with 'amount', 'merchant', 'location', etc.
            context: TransactionContext with user history and velocity.

        Returns:
            FraudDetectionResult with fraud risk and recommended action.
        """
        self.call_count += 1
        self.vector_clock.increment()

        # PATTERN: Context Window Management
        # Limit recent transactions to control context size
        trimmed_context = self._trim_context(context)

        # Estimate tokens: context + transaction
        tokens_estimate = self._estimate_tokens(transaction, trimmed_context)
        total_tokens_used = sum(self.token_usage.values())

        # Check if we have budget remaining
        if total_tokens_used + tokens_estimate > self.config.token_budget:
            # Fall back to basic fraud check (minimal tokens)
            return await self._execute_minimal(
                transaction, trimmed_context, tokens_estimate
            )

        # Normal execution path with full analysis
        return await self._execute_impl(
            transaction, trimmed_context, tokens_estimate
        )

    def _trim_context(self, context: TransactionContext) -> TransactionContext:
        """
        Trim transaction history to control context window size.

        PATTERN: Context Window Management
        Keeps only the last N transactions to prevent unbounded growth.

        Args:
            context: Original transaction context.

        Returns:
            Context with trimmed transaction history.
        """
        trimmed_recent = context.recent_transactions[
            -self.config.max_recent_transactions:
        ]

        return TransactionContext(
            user_id=context.user_id,
            recent_transactions=trimmed_recent,
            average_transaction_value=context.average_transaction_value,
            card_velocity=context.card_velocity
        )

    def _estimate_tokens(
        self,
        transaction: Dict,
        context: TransactionContext
    ) -> int:
        """
        Estimate token consumption for transaction analysis.

        Args:
            transaction: Transaction data.
            context: Transaction context.

        Returns:
            Estimated token count.
        """
        # Base tokens for transaction analysis
        base_tokens = 50

        # Add tokens for context (10 per recent transaction)
        context_tokens = len(context.recent_transactions) * 10

        # Add tokens for reasoning overhead
        reasoning_tokens = 25

        return base_tokens + context_tokens + reasoning_tokens

    async def _execute_impl(
        self,
        transaction: Dict,
        context: TransactionContext,
        tokens_estimate: int
    ) -> FraudDetectionResult:
        """
        Execute full fraud detection analysis.

        PATTERN: Understanding Model Decisions
        Calculates risk score based on multiple factors and provides
        detailed reasoning for the decision.

        Args:
            transaction: Transaction data.
            context: Transaction context.
            tokens_estimate: Estimated token count.

        Returns:
            FraudDetectionResult with detailed risk analysis.
        """
        # Calculate risk score components
        risk_factors = self._calculate_risk_factors(transaction, context)
        fraud_risk = sum(risk_factors.values())
        fraud_risk = min(1.0, fraud_risk)  # Cap at 1.0

        # Determine recommended action
        recommended_action = self._determine_action(fraud_risk)

        # Build reasoning
        reasoning = self._explain_risk(transaction, risk_factors, fraud_risk)

        # Track token usage
        self.token_usage[f"call_{self.call_count}"] = tokens_estimate

        # Create result
        result = FraudDetectionResult(
            fraud_risk=fraud_risk,
            recommended_action=recommended_action,
            reasoning=reasoning,
            tokens_consumed=tokens_estimate,
            vector_clock=VectorClock(
                agent_id=self.config.agent_id,
                timestamp=self.vector_clock.timestamp
            ),
            risk_factors=risk_factors
        )

        return result

    async def _execute_minimal(
        self,
        transaction: Dict,
        context: TransactionContext,
        tokens_estimate: int
    ) -> FraudDetectionResult:
        """
        Execute minimal fraud detection when token budget is exhausted.

        Performs basic amount checking only.

        Args:
            transaction: Transaction data.
            context: Transaction context.
            tokens_estimate: Estimated token count.

        Returns:
            FraudDetectionResult with basic amount-only analysis.
        """
        # Minimal token usage
        minimal_tokens = 10

        amount = transaction.get("amount", 0)
        fraud_risk = 0.0
        risk_factors = {}

        # Only check amount against max
        if amount > self.config.max_transaction_value:
            fraud_risk = 0.5
            risk_factors["amount_exceeds_max"] = 0.5

        recommended_action = self._determine_action(fraud_risk)
        reasoning = (
            f"Token budget constrained. Minimal analysis: "
            f"Amount ${amount} vs max ${self.config.max_transaction_value}. "
            f"Risk: {fraud_risk:.0%}"
        )

        self.token_usage[f"call_{self.call_count}_minimal"] = minimal_tokens

        result = FraudDetectionResult(
            fraud_risk=fraud_risk,
            recommended_action=recommended_action,
            reasoning=reasoning,
            tokens_consumed=minimal_tokens,
            vector_clock=VectorClock(
                agent_id=self.config.agent_id,
                timestamp=self.vector_clock.timestamp
            ),
            risk_factors=risk_factors
        )

        return result

    def _calculate_risk_factors(
        self,
        transaction: Dict,
        context: TransactionContext
    ) -> Dict[str, float]:
        """
        Calculate individual risk factor contributions.

        PATTERN: Understanding Model Decisions
        Breaks down fraud risk into interpretable components.

        Args:
            transaction: Transaction data.
            context: Transaction context.

        Returns:
            Dictionary of risk factor -> contribution (0.0 to 1.0).
        """
        risk_factors = {}

        # Factor 1: Card velocity (transactions per hour)
        if context.card_velocity > 5:
            risk_factors["high_velocity"] = 0.3
        else:
            risk_factors["high_velocity"] = 0.0

        # Factor 2: Transaction amount vs average
        amount = transaction.get("amount", 0)
        avg_amount = context.average_transaction_value

        if avg_amount > 0 and amount > 3 * avg_amount:
            risk_factors["amount_anomaly"] = 0.2
        else:
            risk_factors["amount_anomaly"] = 0.0

        # Factor 3: Amount exceeds configured maximum
        if amount > self.config.max_transaction_value:
            risk_factors["amount_exceeds_max"] = 0.5
        else:
            risk_factors["amount_exceeds_max"] = 0.0

        # Factor 4: Geography anomaly (simplified)
        if self._is_geography_anomaly(transaction, context):
            risk_factors["geography_anomaly"] = 0.2
        else:
            risk_factors["geography_anomaly"] = 0.0

        return risk_factors

    def _is_geography_anomaly(
        self,
        transaction: Dict,
        context: TransactionContext
    ) -> bool:
        """
        Detect if transaction location is anomalous for user.

        Simplified check: if no recent transactions, assume normal.
        If user has location history and this location is new, flag it.

        Args:
            transaction: Transaction data.
            context: Transaction context.

        Returns:
            True if location is anomalous, False otherwise.
        """
        current_location = transaction.get("location", "")
        if not current_location or not context.recent_transactions:
            return False

        # Get locations from recent transactions
        recent_locations = set(
            tx.get("location", "") for tx in context.recent_transactions
            if tx.get("location")
        )

        # If current location not in recent history, it's anomalous
        return current_location not in recent_locations

    def _determine_action(self, fraud_risk: float) -> str:
        """
        Determine recommended action based on fraud risk.

        Args:
            fraud_risk: Fraud risk score (0.0 to 1.0).

        Returns:
            Recommended action: 'allow', 'challenge', or 'block'.
        """
        if fraud_risk < 0.3:
            return RiskAction.ALLOW.value
        elif fraud_risk < self.config.risk_threshold:
            return RiskAction.CHALLENGE.value
        else:
            return RiskAction.BLOCK.value

    def _explain_risk(
        self,
        transaction: Dict,
        risk_factors: Dict[str, float],
        fraud_risk: float
    ) -> str:
        """
        Generate human-readable explanation of fraud risk.

        PATTERN: Understanding Model Decisions
        Provides transparency into how fraud risk was calculated.

        Args:
            transaction: Transaction data.
            risk_factors: Dictionary of risk factor contributions.
            fraud_risk: Overall fraud risk score.

        Returns:
            Human-readable risk explanation.
        """
        amount = transaction.get("amount", 0)
        merchant = transaction.get("merchant", "Unknown")
        location = transaction.get("location", "Unknown")

        # Identify significant risk factors
        significant_factors = [
            (name, score)
            for name, score in risk_factors.items()
            if score > 0
        ]
        significant_factors.sort(key=lambda x: x[1], reverse=True)

        if significant_factors:
            factors_str = ", ".join(
                [f"{name} (+{score:.0%})" for name, score in significant_factors]
            )
            explanation = (
                f"Transaction: ${amount} at {merchant} ({location}). "
                f"Risk factors: {factors_str}. "
                f"Overall fraud risk: {fraud_risk:.0%}. "
                f"Action: {self._determine_action(fraud_risk).upper()}"
            )
        else:
            explanation = (
                f"Transaction: ${amount} at {merchant} ({location}). "
                f"No significant risk factors detected. "
                f"Overall fraud risk: {fraud_risk:.0%}. "
                f"Action: {self._determine_action(fraud_risk).upper()}"
            )

        return explanation

    def get_risk_summary(self) -> Dict:
        """Get summary of fraud detection activity."""
        total_used = sum(self.token_usage.values())
        return {
            "total_calls": self.call_count,
            "total_tokens_used": total_used,
            "token_budget": self.config.token_budget,
            "token_budget_remaining": max(0, self.config.token_budget - total_used),
            "budget_utilization": total_used / self.config.token_budget,
            "call_breakdown": self.token_usage
        }
