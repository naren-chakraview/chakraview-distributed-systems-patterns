"""
Tests for Segmentation Agent.

Tests verify:
1. High-value user classification
2. Dormant user classification
3. Potential user classification
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from segmentation_agent import (
    SegmentationAgent,
    SegmentationConfig,
    UserProfile,
)


@pytest.fixture
def agent():
    """Create segmentation agent."""
    config = SegmentationConfig(
        agent_id="test-segmentation-agent",
        num_segments=4,
        checkpoint_interval=100,
    )
    return SegmentationAgent(config)


def test_segment_high_value_user(agent):
    """
    Test high-value user classification.

    A user with:
    - Lifetime value: $1500
    - Purchase frequency: 10

    Should be classified as high_value with high confidence.
    """
    profile = UserProfile(
        user_id="user_1",
        lifetime_value=1500.0,
        purchase_frequency=10.0,
        product_diversity=0.5,
        churn_risk=0.1,
    )

    result = agent.execute(profile)

    assert result.segment == "high_value"
    assert result.confidence > 0.7
    assert "high_value" in result.reasoning.lower()
    assert "lifetime value" in result.reasoning.lower()


def test_segment_dormant_user(agent):
    """
    Test dormant user classification.

    A user with:
    - Lifetime value: $100
    - Purchase frequency: 0.2

    Should be classified as dormant due to low purchase frequency.
    """
    profile = UserProfile(
        user_id="user_2",
        lifetime_value=100.0,
        purchase_frequency=0.2,
        product_diversity=0.1,
        churn_risk=0.8,
    )

    result = agent.execute(profile)

    assert result.segment == "dormant"
    assert result.confidence > 0.5
    assert "dormant" in result.reasoning.lower()


def test_segment_potential_user(agent):
    """
    Test potential user classification.

    A user with moderate metrics:
    - Lifetime value: $250
    - Purchase frequency: 1.0
    - Product diversity: 0.2

    Should be classified as potential (doesn't fit other segments).
    """
    profile = UserProfile(
        user_id="user_3",
        lifetime_value=250.0,
        purchase_frequency=1.0,
        product_diversity=0.2,
        churn_risk=0.3,
    )

    result = agent.execute(profile)

    assert result.segment == "potential"
    assert result.confidence == 0.5
    assert "potential" in result.reasoning.lower()


def test_segment_loyal_user(agent):
    """
    Test loyal user classification.

    A user with:
    - Purchase frequency: 4.0
    - Product diversity: 0.4

    Should be classified as loyal.
    """
    profile = UserProfile(
        user_id="user_4",
        lifetime_value=600.0,
        purchase_frequency=4.0,
        product_diversity=0.4,
        churn_risk=0.1,
    )

    result = agent.execute(profile)

    assert result.segment == "loyal"
    assert result.confidence > 0.5
    assert "loyal" in result.reasoning.lower()


def test_checkpointing_at_interval(agent):
    """
    Test that checkpointing occurs at configured interval.

    With checkpoint_interval=100, checkpoints should be created
    every 100 processed users.
    """
    # Process 150 users
    for i in range(150):
        profile = UserProfile(
            user_id=f"user_{i}",
            lifetime_value=float(100 + i),
            purchase_frequency=1.0 + (i % 5),
            product_diversity=0.2,
            churn_risk=0.1,
        )
        agent.execute(profile)

    # With interval=100, we should have at least 1 checkpoint
    summary = agent.get_checkpoint_summary()
    assert summary["total_checkpoints"] >= 1
    assert summary["processed_count"] == 150


def test_multiple_segments_in_batch(agent):
    """
    Test that agent correctly classifies different users in sequence.
    """
    users = [
        UserProfile("high_value", 2000.0, 8.0, 0.6, 0.05),  # high_value
        UserProfile("loyal", 500.0, 4.0, 0.5, 0.1),  # loyal
        UserProfile("dormant", 50.0, 0.3, 0.05, 0.9),  # dormant
    ]

    results = [agent.execute(u) for u in users]

    assert results[0].segment == "high_value"
    assert results[1].segment == "loyal"
    assert results[2].segment == "dormant"


def test_confidence_scores_within_range(agent):
    """
    Test that all confidence scores are within valid range [0.0, 1.0].
    """
    users = [
        UserProfile(f"user_{i}", float(100 + i * 50), 1.0 + (i % 5), 0.3, 0.2)
        for i in range(10)
    ]

    results = [agent.execute(u) for u in users]

    for result in results:
        assert 0.0 <= result.confidence <= 1.0
        assert result.segment in ["high_value", "loyal", "dormant", "potential"]


def test_reasoning_includes_metrics(agent):
    """
    Test that reasoning includes relevant metrics from user profile.
    """
    profile = UserProfile(
        user_id="user_test",
        lifetime_value=1500.0,
        purchase_frequency=7.0,
        product_diversity=0.5,
        churn_risk=0.1,
    )

    result = agent.execute(profile)

    # Reasoning should reference relevant metrics
    assert "high_value" in result.reasoning.lower() or "$" in result.reasoning
