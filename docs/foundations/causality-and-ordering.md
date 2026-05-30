# Causality & Ordering in Agent Networks

## Problem Statement

In a distributed agent system, multiple agents may execute concurrently, each making decisions that depend on prior events. When an agent makes a decision at edge, that decision may affect other agents in the cloud. Understanding which decision depends on which prior event — the causal relationship — is critical for debugging, observability, and failure recovery.

Traditional approaches (wall-clock time, request IDs) are insufficient because:
- **Clock skew** — edge devices and cloud clocks may drift; wall-clock time is unreliable
- **Out-of-order delivery** — messages may arrive out of order; wall-clock order doesn't match logical order
- **Concurrency** — multiple agents may execute simultaneously; we need to distinguish causally related events from concurrent ones

How do we track causal dependencies in a distributed agent system?

## Solution Approach

**Happens-Before Relation:** An event A "happens-before" event B if A's result was visible to the agent that executed B. Happens-before defines a partial order over events (some events are ordered, others are concurrent).

**Vector Clocks:** Each agent maintains a vector clock — a map of `{agent_id → logical_timestamp}`. When an agent executes, it increments its own clock. When it sends a message, it includes the vector clock. Recipients merge the received clock with their own, taking the max for each agent.

Example:
```
Agent A at time [A:1, B:0, C:0] sends message to Agent B
Agent B receives message, updates its clock to [A:1, B:1, C:0] (max of received and local)
Agent B's subsequent events are [A:1, B:2, C:0], [A:1, B:3, C:0], etc.

Later, Agent C receives a message from B at [A:1, B:3, C:0]
C's clock becomes [A:1, B:3, C:1]
C now knows: this message is causally dependent on events up to B:3 in Agent B, which includes B's receipt of A's message at A:1
```

**Implementing Causality Tracking:**

1. **Trace context propagation** — attach vector clock to every agent invocation (via trace baggage, headers, or parameters)
2. **Log with vector clock** — include vector clock in structured logs: `{"event": "agent_decision", "agent_id": "A", "vector_clock": {"A": 5, "B": 3, "C": 1}}`
3. **Detect causal dependencies in queries** — queries like "what events preceded this agent's decision?" use vector clock comparison
4. **Reconstruct causal history** — from logs, rebuild the DAG of causally-dependent events for debugging

**Limitations:**
- Vector clocks grow with the number of agents (space: O(n) where n = number of agents)
- For swarms of identical agents, use logical timestamps + agent pool identifiers instead
- For very large systems, use hybrid clocks (wall-clock + logical counter) to compress vector clocks

## When to Use

**Use vector clocks when:**
- You have a small number of agents (< 100) whose identities matter
- You need to reconstruct causal history for debugging
- You're building a distributed transaction system (you need to detect conflicts based on causality)

**Use logical timestamps when:**
- You have many identical agents (agent pool) and don't care which specific instance executed
- You care about total order (even if some events are concurrent, you pick an arbitrary order)
- Simplicity is more important than precision

**Use hybrid clocks when:**
- You have moderate agent counts (10-1000) and want to avoid vector clock inflation
- You need both causal ordering AND wall-clock timestamp

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Vector Clocks** | Precise causality; complete happens-before relation | O(n) space; complex debugging; doesn't directly show wall-clock time |
| **Logical Timestamps** | Simple; works for total ordering | Loses concurrency information; all events appear ordered even if independent |
| **Hybrid Clocks** | Combines causality + wall-clock time; compact | Requires wall-clock synchronization; slightly more complex |
| **Trace IDs + Wall-Clock** | Simple to implement; widely supported | Fails when clocks skew; out-of-order delivery causes confusion |

**Recommendation:** Start with logical timestamps + trace IDs for simplicity. Upgrade to vector clocks if you encounter causality-based bugs (e.g., "why did B make decision X when C hadn't reported the relevant event yet?").

## Observability Hooks

**Metrics to track:**
- **Vector clock size**: Should grow slowly (linear with agent count). If it grows exponentially, check for clock propagation bugs.
- **Causality resolution success rate**: What % of queries can reconstruct full causal history? (Target: 99%+)

**Logs to examine:**
- When an agent makes a surprising decision, check its input messages' vector clocks
- Look for "clock inversion" — Agent B's clock goes backwards (bad; indicates dropped messages or time travel)

**Queries to support:**
- "Show all events causally before this decision" — use vector clock comparison
- "Show all concurrent events (not in happens-before order)" — agents with non-comparable vector clocks
- "Trace causality from edge agent to cloud decision" — follow vector clock evolution across hops

**Distributed tracing integration:**
- Include vector clock in trace baggage for every span
- Use vector clock to tag spans with causal relationships

## Example: Causality in a Multi-Hop Agent System

**Scenario:** Edge agent A makes a measurement, sends it to cloud agent B for inference, which sends decision to agent C for execution.

```
Time    Agent A                  Agent B                 Agent C
----    -------                  -------                 -------
1       [A:1]                    
        (measure)
        
2                   A->[A:1] 
                     (send to B)
                                  Recv [A:1]
                                  [A:1, B:1]
                                  (receive)
                                  
3                                 [A:1, B:2]
                                  (infer)
                                  
4                   B->[A:1, B:2]
                     (send to C)
                                                        Recv [A:1, B:2]
                                                        [A:1, B:2, C:1]
                                                        (receive)

5                                                       [A:1, B:2, C:2]
                                                        (execute)
```

Vector clocks show:
- Event A:1 happens-before B:1 (A:1 was delivered to B)
- B:1 happens-before B:2 (B's own execution is ordered)
- B:2 happens-before C:1 (B's result was delivered to C)
- A:1 transitively happens-before C:2 (through B)

If C's execution failed, we can trace back: C:2 depends on B:2 depends on B:1 depends on A:1. Check A's measurement, B's inference, etc.

## Failure Scenarios

**Clock inversion:** Agent A increments to [A:5, B:3, C:1], then later executes with [A:3, B:5, C:2]. This indicates:
- Dropped messages (B:3 arrived later than expected)
- Time travel or clock reset on an agent
- **Recovery:** Investigate message delivery; check for network partitions; verify clock sources

**Vector clock explosion:** A system with 10 agents generates vector clocks with 10 entries each. Later, it scales to 100 agents, and vector clocks become huge (100 entries).
- **Recovery:** Use agent pool IDs (group identical agents) or switch to hybrid clocks

**Causality cycles:** A's vector clock shows it depends on B:5, B's shows it depends on A:7. This is impossible (cycles in happens-before).
- **Cause:** Usually dropped messages or clock skew
- **Recovery:** Rebuild vector clocks from logs; detect and discard contradictory events

## References

**Classic Papers:**
- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System" — foundational paper on happened-before
- Mattern, F. (1989). "Virtual Time and Global States of Distributed Systems" — vector clocks

**Related Patterns:**
- [Time, Clocks & Synchronization](time-and-clocks.md) — handling clock skew in practice
- [Distributed Tracing](../patterns/observability/distributed-tracing.md) — implementing causality in tracing systems

**Framework Callouts:**
- **LangGraph:** trace_id is basic; use custom metadata for vector clock propagation
- **Crew:** message passing between agents includes implicit ordering; add vector clocks to decision logs
- **Temporal Workflows:** have native causality tracking via workflow history

**Tools:**
- Jaeger (distributed tracing) — can display causal relationships if instrumented correctly
- ElasticSearch with structured logging — query logs by vector clock for causality analysis
