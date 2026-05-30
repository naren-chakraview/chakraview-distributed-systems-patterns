"""
Customer Segmentation Agent with Checkpoint Recovery.

This module demonstrates:
- Checkpointing Agent State (pattern: docs/patterns/failure-recovery/checkpointing.md)
- Understanding Model Decisions (pattern: docs/patterns/observability/understanding-decisions.md)

The agent classifies users into segments (high_value, loyal, dormant, potential)
and checkpoints state at regular intervals for recovery from failures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum


class UserSegment(Enum):
    """Supported user segments."""
    HIGH_VALUE = "high_value"
    LOYAL = "loyal"
    DORMANT = "dormant"
    POTENTIAL = "potential"


@dataclass
class AgentConfig:
    """Base configuration for agents."""
    agent_id: str
    token_budget: int = 1000
    latency_budget_ms: int = 5000


@dataclass
class SegmentationConfig(AgentConfig):
    """Configuration for Segmentation Agent."""
    num_segments: int = 4
    checkpoint_interval: int = 100


@dataclass
class UserProfile:
    """User profile for segmentation."""
    user_id: str
    lifetime_value: float
    purchase_frequency: float
    product_diversity: float
    churn_risk: float


@dataclass
class SegmentationResult:
    """Result of user segmentation."""
    user_id: str
    segment: str
    confidence: float
    reasoning: str
    checkpoint_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SegmentationAgent:
    """
    Customer Segmentation Agent with checkpoint recovery.

    Classifies users into segments based on behavioral metrics and
    maintains checkpoints for failure recovery.
    """

    def __init__(self, config: SegmentationConfig):
        """Initialize the segmentation agent.

        Args:
            config: SegmentationConfig with agent settings.
        """
        self.config = config
        self.processed_count = 0
        self.checkpoints: List[Dict] = []
        self.last_checkpoint_count = 0

    def execute(self, profile: UserProfile) -> SegmentationResult:
        """
        Execute segmentation on a user profile.

        PATTERN: Checkpointing Agent State
        Periodically checkpoints state at checkpoint_interval to enable
        recovery from failures without reprocessing all users.

        Args:
            profile: UserProfile to segment.

        Returns:
            SegmentationResult with segment, confidence, and reasoning.
        """
        self.processed_count += 1

        # Classify the user segment
        segment, confidence, reasoning = self._classify_segment(profile)

        # PATTERN: Checkpointing Agent State
        # Save checkpoint at regular intervals
        if self.processed_count % self.config.checkpoint_interval == 0:
            self._checkpoint_state()

        result = SegmentationResult(
            user_id=profile.user_id,
            segment=segment,
            confidence=confidence,
            reasoning=reasoning,
            checkpoint_count=len(self.checkpoints),
        )

        return result

    def _classify_segment(self, profile: UserProfile) -> Tuple[str, float, str]:
        """
        Classify user into segment based on behavioral metrics.

        PATTERN: Understanding Model Decisions
        Returns segment, confidence, and reasoning for transparency.

        Segment logic:
        - high_value: lifetime_value >= 1000 AND purchase_frequency >= 5
        - loyal: purchase_frequency >= 3 AND product_diversity >= 0.3
        - dormant: purchase_frequency < 0.5 OR churn_risk > 0.7
        - potential: everything else

        Args:
            profile: UserProfile to classify.

        Returns:
            Tuple of (segment_name, confidence, reasoning_str).
        """
        segment = None
        confidence = 0.0
        reasoning = ""

        # Check for high_value segment
        if profile.lifetime_value >= 1000 and profile.purchase_frequency >= 5:
            segment = UserSegment.HIGH_VALUE.value
            confidence = min(
                0.99,
                0.7 + (profile.purchase_frequency / 10.0) * 0.3
            )
            reasoning = (
                f"User classified as {segment}: lifetime value ${profile.lifetime_value:.0f} "
                f"with {profile.purchase_frequency:.1f} purchase frequency."
            )

        # Check for loyal segment
        elif profile.purchase_frequency >= 3 and profile.product_diversity >= 0.3:
            segment = UserSegment.LOYAL.value
            confidence = min(
                0.99,
                0.6 + (profile.product_diversity * 0.3) + (profile.purchase_frequency / 10.0) * 0.1
            )
            reasoning = (
                f"User classified as {segment}: {profile.purchase_frequency:.1f} purchases "
                f"with {profile.product_diversity:.1%} product diversity."
            )

        # Check for dormant segment
        elif profile.purchase_frequency < 0.5 or profile.churn_risk > 0.7:
            segment = UserSegment.DORMANT.value
            confidence = min(
                0.99,
                0.7 + (profile.churn_risk * 0.3)
            )
            reasoning = (
                f"User classified as {segment}: low purchase frequency "
                f"({profile.purchase_frequency:.1f}) or high churn risk ({profile.churn_risk:.1%})."
            )

        # Default to potential segment
        else:
            segment = UserSegment.POTENTIAL.value
            confidence = 0.5
            reasoning = (
                f"User classified as {segment}: moderate engagement metrics "
                f"(LTV: ${profile.lifetime_value:.0f}, frequency: {profile.purchase_frequency:.1f})."
            )

        return segment, confidence, reasoning

    def _checkpoint_state(self) -> None:
        """
        Save agent state checkpoint for failure recovery.

        PATTERN: Checkpointing Agent State
        Logs checkpoint at every checkpoint_interval processed users.
        This enables recovery from failures without reprocessing all users.

        In a production system, this would persist to durable storage
        (e.g., S3, database) to enable recovery.
        """
        checkpoint = {
            "timestamp": datetime.utcnow().isoformat(),
            "processed_count": self.processed_count,
            "checkpoint_number": len(self.checkpoints) + 1,
            "interval": self.config.checkpoint_interval,
        }
        self.checkpoints.append(checkpoint)

    def get_checkpoint_summary(self) -> Dict:
        """Get summary of checkpoint history."""
        return {
            "total_checkpoints": len(self.checkpoints),
            "processed_count": self.processed_count,
            "checkpoint_interval": self.config.checkpoint_interval,
            "checkpoints": self.checkpoints,
        }
