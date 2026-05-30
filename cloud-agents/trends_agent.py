"""
Trends Detection Agent with Distributed Tracing and SLOs.

This module demonstrates:
- Distributed Tracing (pattern: docs/patterns/observability/distributed-tracing.md)
- Causality & Ordering (pattern: docs/foundations/causality-and-ordering.md)
- SLOs for Agentic Workloads (pattern: docs/patterns/predictability/agentic-slos.md)

The agent detects trends in time-series data and provides human-readable
explanations of detected patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class TrendDirection(Enum):
    """Direction of detected trend."""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    STABLE = "stable"


@dataclass
class AgentConfig:
    """Base configuration for agents."""
    agent_id: str
    token_budget: int = 1000
    latency_budget_ms: int = 5000


@dataclass
class TrendsConfig(AgentConfig):
    """Configuration for Trends Agent."""
    window_days: int = 30
    min_data_points: int = 10
    trend_threshold: float = 0.15


@dataclass
class DataPoint:
    """Single data point in time series."""
    timestamp: datetime
    value: float
    metric: str


@dataclass
class TrendDetection:
    """Detected trend."""
    metric: str
    direction: str
    magnitude: float
    confidence: float


@dataclass
class TrendsResult:
    """Result of trends analysis."""
    category: str
    trends: List[Dict[str, Any]]
    explanation: str
    data_points_analyzed: int
    slo_met: bool = True
    trace_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class TrendsAgent:
    """
    Trends Detection Agent with distributed tracing and SLO tracking.

    Detects trends in time-series data with causality ordering and
    provides explanations of detected patterns.
    """

    def __init__(self, config: TrendsConfig):
        """Initialize the trends agent.

        Args:
            config: TrendsConfig with agent settings.
        """
        self.config = config
        self.call_count = 0
        self.slo_violations = 0

    def execute(
        self,
        category: str,
        data_points: List[DataPoint],
        trace_id: Optional[str] = None,
    ) -> TrendsResult:
        """
        Execute trend detection on time-series data.

        PATTERN: Causality & Ordering
        Sorts data_points by timestamp to ensure causal ordering.

        PATTERN: Distributed Tracing
        Accepts trace_id for correlation across distributed systems.

        Args:
            category: Category of data (e.g., "user_visits", "conversion_rate").
            data_points: List of DataPoint with timestamps and values.
            trace_id: Optional trace ID for distributed tracing.

        Returns:
            TrendsResult with detected trends and explanation.
        """
        self.call_count += 1

        return self._execute_impl(category, data_points, trace_id)

    def _execute_impl(
        self,
        category: str,
        data_points: List[DataPoint],
        trace_id: Optional[str] = None,
    ) -> TrendsResult:
        """
        Implementation of trend detection logic.

        PATTERN: Causality & Ordering
        Ensures data is ordered by timestamp before analysis.

        PATTERN: SLOs for Agentic Workloads
        Tracks whether analysis meets latency SLOs.

        Args:
            category: Category of data.
            data_points: List of DataPoint to analyze.
            trace_id: Optional trace ID for distributed tracing.

        Returns:
            TrendsResult with analyzed trends.
        """
        # PATTERN: Causality & Ordering
        # Sort data_points by timestamp to ensure causal order
        sorted_points = sorted(data_points, key=lambda p: p.timestamp)

        # Filter to recent data (window_days)
        cutoff_time = datetime.utcnow() - timedelta(days=self.config.window_days)
        recent_points = [p for p in sorted_points if p.timestamp >= cutoff_time]

        # Check if we have minimum data points
        if len(recent_points) < self.config.min_data_points:
            return TrendsResult(
                category=category,
                trends=[],
                explanation=f"Insufficient data: {len(recent_points)} points (minimum {self.config.min_data_points} required).",
                data_points_analyzed=len(recent_points),
                slo_met=True,
                trace_id=trace_id,
            )

        # Detect trends
        trends = self._detect_trends(category, recent_points)

        # Generate explanation
        explanation = self._explain_trends(category, trends)

        # PATTERN: SLOs for Agentic Workloads
        # In production, would compare actual execution time against SLO
        slo_met = True  # Simplified; real implementation would track timing

        result = TrendsResult(
            category=category,
            trends=trends,
            explanation=explanation,
            data_points_analyzed=len(recent_points),
            slo_met=slo_met,
            trace_id=trace_id,
        )

        return result

    def _detect_trends(self, metric: str, data_points: List[DataPoint]) -> List[Dict[str, Any]]:
        """
        Detect trends in the provided data points.

        Compares value changes over time to identify uptrends, downtrends,
        and stable periods based on trend_threshold.

        Args:
            metric: Metric name being analyzed.
            data_points: Sorted list of DataPoint.

        Returns:
            List of detected trends as dictionaries.
        """
        if len(data_points) < 2:
            return []

        trends = []

        # Calculate overall trend
        first_value = data_points[0].value
        last_value = data_points[-1].value

        if first_value == 0:
            # Avoid division by zero
            magnitude = 0.0
        else:
            magnitude = (last_value - first_value) / first_value

        # Determine trend direction and confidence
        if magnitude > self.config.trend_threshold:
            direction = TrendDirection.UPTREND.value
            confidence = min(0.99, 0.6 + abs(magnitude) * 0.4)
        elif magnitude < -self.config.trend_threshold:
            direction = TrendDirection.DOWNTREND.value
            confidence = min(0.99, 0.6 + abs(magnitude) * 0.4)
        else:
            direction = TrendDirection.STABLE.value
            confidence = min(0.99, 0.5 + (1.0 - abs(magnitude)) * 0.4)

        trend = {
            "metric": metric,
            "direction": direction,
            "magnitude": magnitude,
            "confidence": confidence,
            "start_value": first_value,
            "end_value": last_value,
            "data_points": len(data_points),
        }

        trends.append(trend)

        return trends

    def _explain_trends(self, category: str, trends: List[Dict[str, Any]]) -> str:
        """
        Generate human-readable explanation of detected trends.

        PATTERN: Understanding Model Decisions
        Provides transparency into trend detection reasoning.

        Args:
            category: Category of data.
            trends: List of detected trend dictionaries.

        Returns:
            Human-readable explanation string.
        """
        if not trends:
            return f"No trends detected for category '{category}' in the analysis period."

        trend = trends[0]
        magnitude_pct = trend["magnitude"] * 100
        direction = trend["direction"]

        explanation = (
            f"Category '{category}': {direction} detected with {magnitude_pct:.1f}% change "
            f"(confidence: {trend['confidence']:.0%}). "
            f"Value changed from {trend['start_value']:.2f} to {trend['end_value']:.2f} "
            f"across {trend['data_points']} data points."
        )

        return explanation

    def get_execution_summary(self) -> Dict:
        """Get summary of agent execution."""
        return {
            "total_calls": self.call_count,
            "slo_violations": self.slo_violations,
            "config": {
                "window_days": self.config.window_days,
                "min_data_points": self.config.min_data_points,
                "trend_threshold": self.config.trend_threshold,
            },
        }
