# Time, Clocks & Synchronization

## Problem Statement

Distributed agent systems span multiple devices with independent clocks: edge devices, cloud servers, agents in different regions. Clocks drift (clock skew), jitter, leap seconds. Traditional wall-clock timestamps become unreliable. How do we coordinate timing in an agent system?

## Solution Approach

**Clock Sources:**

1. **Wall-clock time** — system clock; drifts over time; affected by NTP synchronization quality
2. **Monotonic clocks** — always increase; not affected by adjustments; good for measuring durations
3. **Logical clocks** — increment per event (vector clocks, logical timestamps); independent of wall-clock
4. **Hybrid clocks** — combine wall-clock + logical counter; compress vector clocks while preserving causality

**Managing Clock Skew:**

- **Within edge tier** (same network): NTP sync to within 10-100ms; acceptable for most use cases
- **Edge-to-cloud** (WAN): clock skew can be 100ms-1s; use logical clocks + wall-clock validation
- **Timeout detection**: use monotonic clock (doesn't jump backwards); set timeouts with margin (2-3x observed latency)
- **Event ordering**: use happened-before (vector clocks) not wall-clock order

**For Agents:**

- Log events with both wall-clock and monotonic timestamp
- Use monotonic for latency measurements (SLO tracking)
- Use logical clocks for causality (happened-before)
- Use wall-clock only for human-readable timestamps and external timestamps

## When to Use

- Use **wall-clock** for: human-readable logs, correlating with external systems, deadline tracking
- Use **monotonic** for: measuring duration, latency budgets, timeout detection
- Use **logical** for: causality tracking, distributed transactions, state consistency
- Use **hybrid** for: large systems (> 100 agents) needing both causality and wall-clock

## Trade-offs

| Clock Type | Accuracy | Space | Coordination | Use Case |
|-----------|----------|-------|--------------|----------|
| **Wall-clock** | Drifts (NTP-dependent) | 1 entry | Implicit (NTP) | Deadlines, external sync |
| **Monotonic** | Always increases; never backwards | 1 entry | None | Latency measurement |
| **Logical** | Perfect for causality; no wall-clock | O(n) | Piggybacking on messages | Causality tracking |
| **Hybrid** | Good causality + wall-clock | O(n) + 1 | Message piggybacking | Large systems |

## Observability Hooks

**Metrics:**
- Clock skew (max delta across agents; target: < 100ms)
- NTP sync status (% agents in sync)
- Timeout false positives (declared dead but alive)
- Clock inversion (agent clock goes backward)

**Queries:**
- "Which agents have skewed clocks?"
- "What's the wall-clock time when this agent invoked X?"
- "Did a timeout occur due to clock skew?"

## Example: Clock Skew Causing False Timeout

**Scenario:**
- Edge agent requests cloud agent with 5-second timeout
- Cloud clock is 2 seconds ahead of edge (clock skew)
- Edge sends request at wall-clock T=10:00:05
- Cloud receives at wall-clock T=10:00:07 (local)
- Cloud processes for 3 seconds, responds at T=10:00:10
- Edge receives response at T=10:00:08 (local)
- From edge's perspective: took 3 seconds (10:00:08 - 10:00:05); within timeout
- But cloud's clocks show: 10:00:10 - 10:00:07 = 3 seconds

**Prevention:** Use monotonic clocks for timeout measurement; allow clock-skew margin.

## References

- [Causality & Ordering](causality-and-ordering.md)
- [Distributed Tracing](../patterns/observability/distributed-tracing.md)
- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events"
