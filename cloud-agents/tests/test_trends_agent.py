"""
Tests for Trends Agent.

Tests verify:
1. Trend detection with increasing data
2. Handling insufficient data points
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trends_agent import (
    TrendsAgent,
    TrendsConfig,
    DataPoint,
)


@pytest.fixture
def agent():
    """Create trends agent with standard configuration."""
    config = TrendsConfig(
        agent_id="test-trends-agent",
        window_days=30,
        min_data_points=10,
        trend_threshold=0.15,
    )
    return TrendsAgent(config)


def test_trends_detection_increasing(agent):
    """
    Test trend detection with increasing data.

    Creates 10 data points with increasing values representing
    rising user visits. Should detect an uptrend.
    """
    now = datetime.utcnow()
    data_points = [
        DataPoint(
            timestamp=now - timedelta(days=29 - i),
            value=100.0 + (i * 10.0),  # 100, 110, 120, ..., 190
            metric="user_visits"
        )
        for i in range(10)
    ]

    result = agent.execute("user_visits", data_points)

    assert len(result.trends) > 0
    assert result.trends[0]["direction"] == "uptrend"
    assert result.trends[0]["confidence"] > 0.5
    assert result.data_points_analyzed == 10
    assert "uptrend" in result.explanation.lower()


def test_trends_insufficient_data(agent):
    """
    Test handling of insufficient data points.

    With only 1 data point and min_data_points=10, should return
    empty trends and insufficient data explanation.
    """
    now = datetime.utcnow()
    data_points = [
        DataPoint(
            timestamp=now,
            value=100.0,
            metric="conversion_rate"
        )
    ]

    result = agent.execute("conversion_rate", data_points)

    assert len(result.trends) == 0
    assert "insufficient data" in result.explanation.lower()
    assert result.data_points_analyzed == 1
    assert result.slo_met is True


def test_trends_detection_decreasing(agent):
    """
    Test trend detection with decreasing data.

    Creates data points with decreasing values representing
    falling engagement. Should detect a downtrend.
    """
    now = datetime.utcnow()
    data_points = [
        DataPoint(
            timestamp=now - timedelta(days=29 - i),
            value=200.0 - (i * 15.0),  # 200, 185, 170, ..., 65
            metric="engagement_score"
        )
        for i in range(10)
    ]

    result = agent.execute("engagement_score", data_points)

    assert len(result.trends) > 0
    assert result.trends[0]["direction"] == "downtrend"
    assert result.trends[0]["confidence"] > 0.5


def test_trends_stable_data(agent):
    """
    Test trend detection with stable data.

    Creates data points with stable values (within threshold).
    Should detect stable trend.
    """
    now = datetime.utcnow()
    data_points = [
        DataPoint(
            timestamp=now - timedelta(days=29 - i),
            value=100.0,  # Constant value
            metric="system_health"
        )
        for i in range(10)
    ]

    result = agent.execute("system_health", data_points)

    assert len(result.trends) > 0
    assert result.trends[0]["direction"] == "stable"
    assert "stable" in result.explanation.lower()


def test_causality_ordering(agent):
    """
    Test that data points are properly ordered by timestamp.

    Creates data points in random order and verifies the agent
    handles them correctly by sorting.
    """
    now = datetime.utcnow()
    # Create points in non-sequential order (all within 30-day window)
    data_points = [
        DataPoint(timestamp=now - timedelta(days=10), value=120.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=20), value=100.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=5), value=140.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=15), value=110.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=25), value=90.0, metric="metric"),
        DataPoint(timestamp=now, value=150.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=29), value=80.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=3), value=145.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=1), value=148.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=7), value=130.0, metric="metric"),
    ]

    result = agent.execute("metric", data_points)

    # Should successfully process despite unordered input
    assert result.data_points_analyzed == 10
    assert len(result.trends) > 0
    # Should detect uptrend from 80 to 150
    assert result.trends[0]["direction"] == "uptrend"


def test_window_days_filtering(agent):
    """
    Test that only data within window_days is considered.

    Creates old data (outside 30-day window) and recent data (inside).
    Only recent data should be analyzed.
    """
    now = datetime.utcnow()
    data_points = [
        # Old data (outside 30-day window)
        DataPoint(timestamp=now - timedelta(days=60), value=50.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=50), value=55.0, metric="metric"),
        # Recent data (inside 30-day window) - 10 points to meet min_data_points
        DataPoint(timestamp=now - timedelta(days=28), value=100.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=24), value=102.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=20), value=105.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=16), value=108.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=12), value=110.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=8), value=115.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=4), value=120.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=2), value=122.0, metric="metric"),
        DataPoint(timestamp=now - timedelta(days=1), value=123.0, metric="metric"),
        DataPoint(timestamp=now, value=125.0, metric="metric"),
    ]

    result = agent.execute("metric", data_points)

    # Should only include recent points (outside 30-day window excluded)
    assert result.data_points_analyzed >= 10
    assert len(result.trends) > 0
    assert result.trends[0]["start_value"] >= 100.0


def test_trace_id_propagation(agent):
    """
    Test that trace ID is propagated through execution.

    PATTERN: Distributed Tracing
    """
    now = datetime.utcnow()
    data_points = [
        DataPoint(timestamp=now - timedelta(days=29 - i), value=100.0 + i * 5, metric="metric")
        for i in range(10)
    ]

    trace_id = "test-trace-12345"
    result = agent.execute("metric", data_points, trace_id=trace_id)

    assert result.trace_id == trace_id


def test_explanation_quality(agent):
    """
    Test that explanation includes relevant information.

    PATTERN: Understanding Model Decisions
    """
    now = datetime.utcnow()
    data_points = [
        DataPoint(
            timestamp=now - timedelta(days=29 - i),
            value=100.0 + (i * 20.0),
            metric="revenue"
        )
        for i in range(10)
    ]

    result = agent.execute("revenue", data_points)

    # Explanation should include:
    # - category name
    # - trend direction
    # - confidence
    # - start and end values
    assert "revenue" in result.explanation.lower()
    assert "uptrend" in result.explanation.lower()
    assert "confidence" in result.explanation.lower()
    assert "100.00" in result.explanation  # start value
    assert "280.00" in result.explanation  # end value


def test_execution_summary(agent):
    """
    Test that execution summary tracks calls.
    """
    now = datetime.utcnow()
    data_points = [
        DataPoint(timestamp=now - timedelta(days=29 - i), value=100.0 + i, metric="m")
        for i in range(10)
    ]

    agent.execute("m1", data_points)
    agent.execute("m2", data_points)

    summary = agent.get_execution_summary()

    assert summary["total_calls"] == 2
    assert summary["config"]["window_days"] == 30
    assert summary["config"]["min_data_points"] == 10
