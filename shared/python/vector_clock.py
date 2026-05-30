"""Vector Clock implementation for distributed causality tracking.

Pattern: Causality & Ordering (see docs/foundations/causality-and-ordering.md)
Provides a simple logical clock mechanism to track causal dependencies between events
in a distributed system without relying on wall-clock time.
"""

from typing import Dict, Optional
from shared.python_gen.shared.proto import messages_pb2


class VectorClock:
    """Tracks logical causality between distributed agents.

    A vector clock is a dictionary mapping agent IDs to logical timestamps.
    It allows us to determine if events are causally related or concurrent,
    which is essential for maintaining consistency in distributed systems.
    """

    def __init__(self, clock: Optional[Dict[str, int]] = None):
        """Initialize a VectorClock.

        Args:
            clock: Optional dict of {agent_id: timestamp}. Defaults to empty dict.
        """
        self.clock = clock or {}

    @classmethod
    def from_proto(cls, proto_vc: messages_pb2.VectorClock) -> "VectorClock":
        """Create a VectorClock from a protobuf message.

        Args:
            proto_vc: A messages_pb2.VectorClock protobuf message.

        Returns:
            A new VectorClock instance with the same clock values.
        """
        return cls(clock=dict(proto_vc.clock))

    def to_proto(self) -> messages_pb2.VectorClock:
        """Convert this VectorClock to a protobuf message.

        Returns:
            A messages_pb2.VectorClock protobuf message.
        """
        proto_vc = messages_pb2.VectorClock()
        proto_vc.clock.update(self.clock)
        return proto_vc

    def increment(self, agent_id: str) -> None:
        """Increment the logical timestamp for an agent.

        Called when an agent performs a local action or sends a message.

        Args:
            agent_id: The ID of the agent performing the action.
        """
        if agent_id not in self.clock:
            self.clock[agent_id] = 0
        self.clock[agent_id] += 1

    def merge(self, other: "VectorClock") -> None:
        """Merge another VectorClock into this one (pointwise maximum).

        Called when an agent receives a message with a vector clock.
        Takes the maximum timestamp for each agent.

        Args:
            other: Another VectorClock to merge in.
        """
        for agent_id, timestamp in other.clock.items():
            if agent_id not in self.clock:
                self.clock[agent_id] = timestamp
            else:
                self.clock[agent_id] = max(self.clock[agent_id], timestamp)

    def happens_before(self, other: "VectorClock") -> bool:
        """Check if this VectorClock happens before another (strict causality).

        Returns True if all timestamps in self are <= those in other,
        and at least one is strictly less.

        Args:
            other: Another VectorClock to compare with.

        Returns:
            True if this clock happens before other, False otherwise.
        """
        less_or_equal = True
        strictly_less = False

        # Check all agents in self
        for agent_id, ts in self.clock.items():
            other_ts = other.clock.get(agent_id, 0)
            if ts > other_ts:
                return False
            if ts < other_ts:
                strictly_less = True

        # Check if other has agents not in self with positive timestamps
        for agent_id, ts in other.clock.items():
            if agent_id not in self.clock and ts > 0:
                strictly_less = True

        return strictly_less and less_or_equal

    def concurrent_with(self, other: "VectorClock") -> bool:
        """Check if this VectorClock is concurrent with another (no causal ordering).

        Returns True if neither happens before the other.

        Args:
            other: Another VectorClock to compare with.

        Returns:
            True if the clocks are concurrent, False otherwise.
        """
        return not (self.happens_before(other) or other.happens_before(self))

    def __repr__(self) -> str:
        """Return a string representation of the VectorClock."""
        return f"VectorClock({self.clock})"
