# Reservation vs. Burst Allocation

## Problem Statement

Do we guarantee resources to agents upfront (reservation), or allocate on-demand (burst)? Reservation guarantees predictability but wastes resources. Burst is efficient but unpredictable. How do we balance?

## Solution Approach

**Reservation (Guaranteed Minimum):**

```
Agent A reserved: 500 tokens/sec minimum guaranteed
Agent B reserved: 300 tokens/sec minimum guaranteed
Remaining capacity: 1000 - 800 = 200 tokens/sec (burst pool)

Peak load:
- Agent A uses 500 (guaranteed)
- Agent B uses 300 (guaranteed)
- Agent A can burst up to +100 from burst pool
- Agent B can burst up to +100 from burst pool
- Total: 500 + 300 + 100 + 100 = 1000 (full capacity)
```

**Burst (On-Demand):**

```
No reservation; agents compete for available resources
Available: 1000 tokens/sec
- If Agent A + B idle, Agent C can burst to 1000
- If Agent A needs 500, Agent B gets remaining 500
- No fairness guarantee; depends on arrival order
```

**Hybrid (Reservation + Burst):**

```
Reservation phase: allocate minimums
- Agent A: 500 (guaranteed)
- Agent B: 300 (guaranteed)
- Total reserved: 800

Burst phase: allocate remaining capacity
- Burst pool: 200 tokens/sec (unused capacity)
- Agents can request burst up to their limit
- If multiple agents burst, use WFQ to fairly share

Benefits:
- Agents get guaranteed minimum (predictable)
- Unused capacity available for bursting (efficient)
```

## When to Use

- Use **reservation** for: critical agents (payment), SLA-critical workflows
- Use **burst** for: experimental agents, batch processing
- Use **hybrid** for: mixed workloads (critical + batch)

## Trade-offs

| Approach | Predictability | Efficiency | Fairness |
|----------|----------------|-----------|----------|
| **Reservation** | Very high (guaranteed) | Low (may waste) | High (fair allocation) |
| **Burst** | Low (unpredictable) | Very high (no waste) | Low (first-come-first-served) |
| **Hybrid** | High (guaranteed minimum) | High (burst available) | High (reserved + fair burst) |

**Recommendation:** Use hybrid; set reservations based on SLA; allocate burst fairly.

## Observability Hooks

**Metrics:**
- Reservation utilization (actual / reserved)
- Burst usage (bursting frequency)
- Unused capacity (waste)

**Queries:**
- "Which agents frequently burst?"
- "Reservation over-provisioned?" (if utilization < 80%)

## References

- [Fair Queuing & Scheduling](fair-queuing.md)
- [Context Window Allocation](context-allocation.md)
