#!/usr/bin/env python3
"""
Demo: Causality and Vector Clocks

Demonstrates how vector clocks track causality in distributed agent systems.

Pattern: docs/foundations/causality-and-ordering.md
Pattern: docs/patterns/observability/distributed-tracing.md

This demo shows:
1. Vector clock incrementing within agents
2. Vector clock merging when messages cross agents
3. Causal relationships between events
4. Detecting concurrent vs. causally-ordered events
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class EventType(Enum):
    """Types of events in distributed agents."""
    LOCAL_EXECUTION = "local_execution"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    DECISION = "decision"


@dataclass
class VectorClock:
    """
    Vector Clock for tracking causality.

    PATTERN: Time and Clocks
    Tracks logical time in distributed systems. Each agent has its own
    clock value, and the full vector tracks causality across agents.
    """

    clock: Dict[str, int] = field(default_factory=dict)

    def increment(self, agent_id: str) -> None:
        """Increment this agent's clock."""
        if agent_id not in self.clock:
            self.clock[agent_id] = 0
        self.clock[agent_id] += 1

    def merge(self, other: "VectorClock") -> None:
        """
        Merge with another vector clock.

        PATTERN: Causality and Ordering
        When an agent receives a message, it merges the sender's clock
        with its own, establishing the happened-before relationship.
        """
        for agent_id, timestamp in other.clock.items():
            if agent_id not in self.clock:
                self.clock[agent_id] = timestamp
            else:
                self.clock[agent_id] = max(self.clock[agent_id], timestamp)

    def compare(self, other: "VectorClock") -> str:
        """Compare two vector clocks for causality."""
        # Check if self < other (all values <=, at least one <)
        self_less_equal = all(
            self.clock.get(a, 0) <= other.clock.get(a, 0)
            for a in set(self.clock.keys()) | set(other.clock.keys())
        )
        self_less = any(
            self.clock.get(a, 0) < other.clock.get(a, 0)
            for a in set(self.clock.keys()) | set(other.clock.keys())
        )

        # Check if other < self
        other_less_equal = all(
            other.clock.get(a, 0) <= self.clock.get(a, 0)
            for a in set(self.clock.keys()) | set(other.clock.keys())
        )
        other_less = any(
            other.clock.get(a, 0) < self.clock.get(a, 0)
            for a in set(self.clock.keys()) | set(other.clock.keys())
        )

        if self_less_equal and self_less:
            return "HAPPENED_BEFORE"  # self -> other
        elif other_less_equal and other_less:
            return "HAPPENED_AFTER"  # other -> self
        else:
            return "CONCURRENT"  # Neither happens before the other

    def copy(self) -> "VectorClock":
        """Create a copy of this vector clock."""
        return VectorClock(clock=self.clock.copy())

    def __str__(self) -> str:
        """String representation."""
        items = [f"{k}:{v}" for k, v in sorted(self.clock.items())]
        return "{" + ", ".join(items) + "}"


@dataclass
class Event:
    """An event in an agent's execution."""

    event_id: str
    agent_id: str
    event_type: EventType
    description: str
    vector_clock: VectorClock = field(default_factory=VectorClock)
    data: Dict = field(default_factory=dict)


class DistributedAgent:
    """An agent in a distributed system."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.vector_clock = VectorClock()
        self.vector_clock.increment(agent_id)
        self.events: List[Event] = []
        self.event_counter = 0

    def execute_local_decision(self, description: str, data: Dict = None) -> Event:
        """Execute a local decision."""
        self.event_counter += 1

        # Increment clock for this local event
        self.vector_clock.increment(self.agent_id)

        event = Event(
            event_id=f"{self.agent_id}_event_{self.event_counter}",
            agent_id=self.agent_id,
            event_type=EventType.LOCAL_EXECUTION,
            description=description,
            vector_clock=self.vector_clock.copy(),
            data=data or {},
        )

        self.events.append(event)
        return event

    def make_decision(self, decision_text: str) -> Event:
        """Make a decision."""
        self.event_counter += 1

        # Increment clock for this decision
        self.vector_clock.increment(self.agent_id)

        event = Event(
            event_id=f"{self.agent_id}_event_{self.event_counter}",
            agent_id=self.agent_id,
            event_type=EventType.DECISION,
            description=decision_text,
            vector_clock=self.vector_clock.copy(),
        )

        self.events.append(event)
        return event

    def receive_message(self, sender_clock: VectorClock, message: str) -> Event:
        """Receive a message from another agent."""
        self.event_counter += 1

        # Merge clocks: establish causality
        self.vector_clock.merge(sender_clock)
        # Increment own clock after merge
        self.vector_clock.increment(self.agent_id)

        event = Event(
            event_id=f"{self.agent_id}_event_{self.event_counter}",
            agent_id=self.agent_id,
            event_type=EventType.MESSAGE_RECEIVED,
            description=f"Received: {message}",
            vector_clock=self.vector_clock.copy(),
            data={"sender_clock": sender_clock.copy()},
        )

        self.events.append(event)
        return event

    def send_message(self, message: str) -> tuple:
        """Send a message with vector clock."""
        self.event_counter += 1

        # Increment clock before sending
        self.vector_clock.increment(self.agent_id)

        event = Event(
            event_id=f"{self.agent_id}_event_{self.event_counter}",
            agent_id=self.agent_id,
            event_type=EventType.MESSAGE_SENT,
            description=f"Sending: {message}",
            vector_clock=self.vector_clock.copy(),
        )

        self.events.append(event)
        return event, self.vector_clock.copy()

    def print_timeline(self) -> None:
        """Print agent's event timeline."""
        print(f"\nAgent: {self.agent_id}")
        print("-" * 60)
        for i, event in enumerate(self.events, 1):
            print(f"{i}. {event.event_type.value}: {event.description}")
            print(f"   Clock: {event.vector_clock}")
            print(f"   Event ID: {event.event_id}")


def main():
    """Run causality demo."""
    print("=" * 70)
    print("CAUSALITY AND VECTOR CLOCKS DEMO")
    print("=" * 70)
    print()

    print("Scenario: Multi-agent fraud detection pipeline")
    print("Agents: Intent (edge), Fraud (edge), Segmentation (cloud)")
    print()

    # Create agents
    intent_agent = DistributedAgent("intent-edge")
    fraud_agent = DistributedAgent("fraud-edge")
    segment_agent = DistributedAgent("segment-cloud")

    print("=" * 70)
    print("PHASE 1: Local Execution (No Communication)")
    print("=" * 70)

    # Intent agent processes message
    intent_event1 = intent_agent.execute_local_decision("Process user message")
    print(f"\n[Intent] Processed message - Clock: {intent_event1.vector_clock}")

    intent_event2 = intent_agent.make_decision("Intent: PURCHASE")
    print(f"[Intent] Made decision - Clock: {intent_event2.vector_clock}")

    # Fraud agent independently processes
    fraud_event1 = fraud_agent.execute_local_decision("Fetch transaction data")
    print(f"\n[Fraud] Fetched data - Clock: {fraud_event1.vector_clock}")

    fraud_event2 = fraud_agent.make_decision("Risk: LOW")
    print(f"[Fraud] Made decision - Clock: {fraud_event2.vector_clock}")

    print("\nObservation: Both agents have independent clocks")
    print("Events are CONCURRENT (no happened-before relation)")

    print()
    print("=" * 70)
    print("PHASE 2: Communication (Establishing Causality)")
    print("=" * 70)

    # Intent sends result to Fraud
    print("\n[Intent] Sending intent result to Fraud...")
    intent_send_event, intent_clock_at_send = intent_agent.send_message(
        "Intent detection: PURCHASE"
    )
    print(f"Intent clock at send: {intent_clock_at_send}")

    # Fraud receives from Intent
    print(f"\n[Fraud] Receiving message from Intent...")
    fraud_receive_event = fraud_agent.receive_message(
        intent_clock_at_send, "Received intent: PURCHASE"
    )
    print(f"Fraud clock before receive: {fraud_event2.vector_clock}")
    print(f"Fraud clock after receive: {fraud_receive_event.vector_clock}")

    # Fraud makes decision based on intent
    fraud_event3 = fraud_agent.make_decision("Updated risk: LOW (confirmed by intent)")
    print(f"Fraud clock after decision: {fraud_event3.vector_clock}")

    print("\nObservation: Fraud's clock now includes Intent's values")
    print("Event causality established: Intent -> Fraud")

    print()
    print("=" * 70)
    print("PHASE 3: Cloud Analysis (Multi-Hop Communication)")
    print("=" * 70)

    # Fraud sends to Segmentation
    print("\n[Fraud] Sending fraud result to Segmentation...")
    fraud_send_event, fraud_clock_at_send = fraud_agent.send_message(
        "Fraud analysis complete: LOW risk"
    )
    print(f"Fraud clock at send: {fraud_clock_at_send}")

    # Segmentation receives from Fraud
    print(f"\n[Segment] Receiving message from Fraud...")
    segment_receive_event = segment_agent.receive_message(
        fraud_clock_at_send, "Received fraud result: LOW risk"
    )
    print(f"Segment clock before receive: {segment_agent.vector_clock}")
    print(f"Segment clock after receive: {segment_receive_event.vector_clock}")

    # Segmentation makes decision
    segment_event = segment_agent.make_decision("Assigned segment: PREMIUM")
    print(f"Segment clock after decision: {segment_event.vector_clock}")

    print("\nObservation: Segmentation's clock includes both Intent and Fraud values")
    print("Full causality chain: Intent -> Fraud -> Segmentation")

    print()
    print("=" * 70)
    print("CAUSALITY ANALYSIS")
    print("=" * 70)

    # Compare events
    print(f"\nCompare Intent Event 2 vs Fraud Event 1:")
    comparison = intent_event2.vector_clock.compare(fraud_event1.vector_clock)
    print(f"  Relationship: {comparison}")

    print(f"\nCompare Intent Event 2 vs Fraud Event 3:")
    comparison = intent_event2.vector_clock.compare(fraud_event3.vector_clock)
    print(f"  Relationship: {comparison}")

    print(f"\nCompare Fraud Event 1 vs Segment Event:")
    comparison = fraud_event1.vector_clock.compare(segment_event.vector_clock)
    print(f"  Relationship: {comparison}")

    print()
    print("=" * 70)
    print("EVENT TIMELINES")
    print("=" * 70)

    intent_agent.print_timeline()
    fraud_agent.print_timeline()
    segment_agent.print_timeline()

    print()
    print("=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print()
    print("1. Vector clocks track logical time, not wall-clock time")
    print("2. Local events increment own clock value")
    print("3. Receiving a message merges clocks, establishing causality")
    print("4. Final clock includes values from all previous agents")
    print("5. Concurrent events have incomparable vector clocks")
    print("6. Causal chains are visible in the clock progression")
    print()
    print("Applications:")
    print("- Detect which agent made a critical decision")
    print("- Reconstruct causality for debugging")
    print("- Identify concurrent operations (can parallelize)")
    print("- Implement consistent snapshots of distributed state")
    print()
    print("Pattern Documentation:")
    print("- Causality & Ordering: docs/foundations/causality-and-ordering.md")
    print("- Time and Clocks: docs/foundations/time-and-clocks.md")
    print("- Distributed Tracing: docs/patterns/observability/distributed-tracing.md")


if __name__ == "__main__":
    main()
