"""
Tests for Fraud Detection Agent.

Tests verify:
1. Normal transaction handling (allow)
2. High velocity detection (challenge/block)
3. Amount limit enforcement (block)
"""

import pytest
from edge_agents.fraud_agent import (
    FraudDetectionAgent,
    FraudDetectionConfig,
    TransactionContext,
    RiskAction,
)


@pytest.fixture
def agent_normal():
    """Create agent with standard configuration."""
    config = FraudDetectionConfig(
        agent_id="test-fraud-agent",
        token_budget=5000,
        risk_threshold=0.7,
        max_transaction_value=1000,
        alert_cooldown_minutes=5,
        max_recent_transactions=10,
    )
    return FraudDetectionAgent(config)


@pytest.mark.asyncio
async def test_fraud_detection_normal_transaction(agent_normal):
    """
    Test fraud detection for normal transaction.

    A normal $50 transaction with average history should be allowed.
    """
    transaction = {
        "amount": 50,
        "merchant": "Local Store",
        "location": "New York",
    }

    context = TransactionContext(
        user_id="user123",
        recent_transactions=[
            {"amount": 45, "merchant": "Local Store", "location": "New York"},
            {"amount": 60, "merchant": "Coffee Shop", "location": "New York"},
            {"amount": 55, "merchant": "Gas Station", "location": "New York"},
        ],
        average_transaction_value=50.0,
        card_velocity=2,  # 2 transactions per hour
    )

    result = await agent_normal.execute(transaction, context)

    # Normal transaction should be allowed
    assert result.recommended_action == RiskAction.ALLOW.value
    assert result.fraud_risk < 0.3
    assert result.tokens_consumed > 0
    assert "Local Store" in result.reasoning
    assert "ALLOW" in result.reasoning.upper()


@pytest.mark.asyncio
async def test_fraud_detection_high_velocity(agent_normal):
    """
    Test fraud detection for high card velocity.

    10 transactions per hour with $200 amount (4x average)
    should trigger risk > 0.25.
    """
    transaction = {
        "amount": 200,
        "merchant": "Electronics Store",
        "location": "New York",
    }

    context = TransactionContext(
        user_id="user456",
        recent_transactions=[
            {"amount": 50, "merchant": "Store A", "location": "New York"},
            {"amount": 55, "merchant": "Store B", "location": "New York"},
            {"amount": 48, "merchant": "Store C", "location": "New York"},
            {"amount": 52, "merchant": "Store D", "location": "New York"},
            {"amount": 49, "merchant": "Store E", "location": "New York"},
        ],
        average_transaction_value=50.0,
        card_velocity=10,  # 10 transactions per hour - HIGH VELOCITY
    )

    result = await agent_normal.execute(transaction, context)

    # High velocity + anomalous amount should trigger challenge/block
    assert result.fraud_risk >= 0.25
    # Risk should come from velocity + amount anomaly
    assert result.risk_factors.get("high_velocity", 0) > 0
    assert result.risk_factors.get("amount_anomaly", 0) > 0
    assert result.tokens_consumed > 0
    assert "200" in result.reasoning


@pytest.mark.asyncio
async def test_fraud_detection_blocks_over_limit(agent_normal):
    """
    Test that transactions over the limit are blocked.

    A $5,000 transaction (over $1,000 limit) should be blocked.
    """
    transaction = {
        "amount": 5000,
        "merchant": "Luxury Store",
        "location": "New York",
    }

    context = TransactionContext(
        user_id="user789",
        recent_transactions=[
            {"amount": 100, "merchant": "Store", "location": "New York"},
            {"amount": 120, "merchant": "Store", "location": "New York"},
        ],
        average_transaction_value=110.0,
        card_velocity=1,
    )

    result = await agent_normal.execute(transaction, context)

    # Transaction exceeding max should be blocked
    assert result.recommended_action == RiskAction.BLOCK.value
    assert result.fraud_risk >= agent_normal.config.risk_threshold
    assert result.risk_factors.get("amount_exceeds_max", 0) == 0.5
    assert "5000" in result.reasoning or "BLOCK" in result.reasoning


