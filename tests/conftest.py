"""Pytest configuration and fixtures for integration tests.

Provides fixtures for all agent types used in the reference implementation:
- IntentDetectionAgent (edge)
- FraudDetectionAgent (edge)
- TrendsAnalysisAgent (cloud)
- SegmentationAgent (cloud)
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
from enum import Enum


class IntentCategory(Enum):
    """Supported intent categories."""
    PURCHASE = "purchase"
    SUPPORT = "support"
    INQUIRY = "inquiry"
    FEEDBACK = "feedback"
    OTHER = "other"


class RiskLevel(Enum):
    """Risk levels for fraud detection."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentConfig:
    """Base configuration for agents."""
    agent_id: str
    token_budget: int = 1000
    latency_budget_ms: int = 5000


@dataclass
class VectorClock:
    """Vector clock for causal ordering."""
    agent_id: str
    timestamp: int = 0

    def increment(self):
        """Increment the clock."""
        self.timestamp += 1

    def merge(self, other):
        """Merge with another vector clock."""
        self.timestamp = max(self.timestamp, other.timestamp)

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


@dataclass
class FraudDetectionResult:
    """Result of fraud detection."""
    risk_level: str
    risk_score: float
    factors: List[str]
    reasoning: str
    tokens_consumed: int
    vector_clock: VectorClock
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrendsAnalysisResult:
    """Result of trends analysis."""
    trend: str
    velocity: float
    direction: str
    reasoning: str
    tokens_consumed: int
    vector_clock: VectorClock
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SegmentationResult:
    """Result of customer segmentation."""
    segment: str
    confidence: float
    characteristics: Dict[str, float]
    reasoning: str
    tokens_consumed: int
    vector_clock: VectorClock
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MockIntentAgent:
    """Mock Intent Detection Agent for testing."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.vector_clock = VectorClock(agent_id=config.agent_id)
        self.call_count = 0
        self.token_usage = {}

    async def execute(self, message: str) -> IntentDetectionResult:
        """Mock intent detection execution."""
        self.call_count += 1
        self.vector_clock.increment()

        tokens_estimate = max(1, len(message) // 4)
        self.token_usage[f"call_{self.call_count}"] = tokens_estimate

        # Simple mock: detect purchase if "buy" in message
        intent = IntentCategory.PURCHASE.value if "buy" in message.lower() else IntentCategory.INQUIRY.value
        confidence = 0.85 if intent == IntentCategory.PURCHASE.value else 0.75

        return IntentDetectionResult(
            intent=intent,
            confidence=confidence,
            reasoning=f"Mock detection for: {message[:50]}",
            tokens_consumed=tokens_estimate,
            vector_clock=VectorClock(agent_id=self.config.agent_id, timestamp=self.vector_clock.timestamp),
            degraded=False
        )


class MockFraudAgent:
    """Mock Fraud Detection Agent for testing."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.vector_clock = VectorClock(agent_id=config.agent_id)
        self.call_count = 0
        self.token_usage = {}

    async def execute(self, transaction_data: Dict) -> FraudDetectionResult:
        """Mock fraud detection execution."""
        self.call_count += 1
        self.vector_clock.increment()

        tokens_estimate = max(1, len(str(transaction_data)) // 4)
        self.token_usage[f"call_{self.call_count}"] = tokens_estimate

        # Simple mock: high risk if amount > 5000
        amount = transaction_data.get("amount", 0)
        risk_level = RiskLevel.HIGH.value if amount > 5000 else RiskLevel.LOW.value
        risk_score = 0.8 if amount > 5000 else 0.2

        return FraudDetectionResult(
            risk_level=risk_level,
            risk_score=risk_score,
            factors=["amount", "location"] if amount > 5000 else ["baseline"],
            reasoning=f"Mock fraud analysis for amount: {amount}",
            tokens_consumed=tokens_estimate,
            vector_clock=VectorClock(agent_id=self.config.agent_id, timestamp=self.vector_clock.timestamp)
        )


class MockTrendsAgent:
    """Mock Trends Analysis Agent for testing."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.vector_clock = VectorClock(agent_id=config.agent_id)
        self.call_count = 0
        self.token_usage = {}

    async def execute(self, metrics_data: Dict) -> TrendsAnalysisResult:
        """Mock trends analysis execution."""
        self.call_count += 1
        self.vector_clock.increment()

        tokens_estimate = max(1, len(str(metrics_data)) // 4)
        self.token_usage[f"call_{self.call_count}"] = tokens_estimate

        trend_value = metrics_data.get("current_metric", 100)
        previous_value = metrics_data.get("previous_metric", 90)

        direction = "up" if trend_value > previous_value else "down"
        velocity = abs(trend_value - previous_value) / max(previous_value, 1)

        return TrendsAnalysisResult(
            trend="growth" if direction == "up" else "decline",
            velocity=velocity,
            direction=direction,
            reasoning=f"Mock trends: {trend_value} vs {previous_value}",
            tokens_consumed=tokens_estimate,
            vector_clock=VectorClock(agent_id=self.config.agent_id, timestamp=self.vector_clock.timestamp)
        )


class MockSegmentationAgent:
    """Mock Segmentation Agent for testing."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.vector_clock = VectorClock(agent_id=config.agent_id)
        self.call_count = 0
        self.token_usage = {}

    async def execute(self, customer_data: Dict) -> SegmentationResult:
        """Mock segmentation execution."""
        self.call_count += 1
        self.vector_clock.increment()

        tokens_estimate = max(1, len(str(customer_data)) // 4)
        self.token_usage[f"call_{self.call_count}"] = tokens_estimate

        # Simple mock: high-value if spend > 1000
        spend = customer_data.get("lifetime_spend", 0)
        segment = "premium" if spend > 1000 else "standard"
        confidence = 0.9 if spend > 1000 else 0.85

        return SegmentationResult(
            segment=segment,
            confidence=confidence,
            characteristics={"spend": float(spend), "activity": 0.7},
            reasoning=f"Mock segmentation for spend: {spend}",
            tokens_consumed=tokens_estimate,
            vector_clock=VectorClock(agent_id=self.config.agent_id, timestamp=self.vector_clock.timestamp)
        )


@pytest.fixture
def intent_agent_config():
    """Fixture for intent agent configuration."""
    return AgentConfig(agent_id="intent-edge-1", token_budget=5000)


@pytest.fixture
def fraud_agent_config():
    """Fixture for fraud agent configuration."""
    return AgentConfig(agent_id="fraud-edge-1", token_budget=5000)


@pytest.fixture
def trends_agent_config():
    """Fixture for trends agent configuration."""
    return AgentConfig(agent_id="trends-cloud-1", token_budget=10000)


@pytest.fixture
def segmentation_agent_config():
    """Fixture for segmentation agent configuration."""
    return AgentConfig(agent_id="segmentation-cloud-1", token_budget=10000)


@pytest.fixture
def intent_agent(intent_agent_config):
    """Fixture for intent detection agent."""
    return MockIntentAgent(intent_agent_config)


@pytest.fixture
def fraud_agent(fraud_agent_config):
    """Fixture for fraud detection agent."""
    return MockFraudAgent(fraud_agent_config)


@pytest.fixture
def trends_agent(trends_agent_config):
    """Fixture for trends analysis agent."""
    return MockTrendsAgent(trends_agent_config)


@pytest.fixture
def segmentation_agent(segmentation_agent_config):
    """Fixture for segmentation agent."""
    return MockSegmentationAgent(segmentation_agent_config)


@pytest.fixture
def sample_user_message():
    """Fixture for sample user message."""
    return "I want to buy a new laptop for work, what options do you have?"


@pytest.fixture
def sample_transaction():
    """Fixture for sample transaction data."""
    return {
        "transaction_id": "txn_123456",
        "amount": 2500.00,
        "currency": "USD",
        "merchant": "electronics_store",
        "location": "US",
        "timestamp": "2026-05-29T10:30:00Z"
    }


@pytest.fixture
def sample_metrics():
    """Fixture for sample metrics data."""
    return {
        "current_metric": 125.5,
        "previous_metric": 110.2,
        "metric_name": "user_engagement",
        "period": "daily"
    }


@pytest.fixture
def sample_customer():
    """Fixture for sample customer data."""
    return {
        "customer_id": "cust_789",
        "lifetime_spend": 5000.00,
        "purchase_frequency": "monthly",
        "region": "US-West",
        "account_age_days": 365
    }
