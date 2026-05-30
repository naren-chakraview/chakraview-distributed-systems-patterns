# Single-Agent at Scale

## Problem Statement

One agent handles many requests: edge agent serves 1000 concurrent users, cloud inference handles 100 RPS. How do we replicate, load-balance, and coordinate stateless agents at scale?

## Solution Approach

**Stateless Replication:**

```
Load Balancer
  ├─ Agent Instance 1 (edge1, availability zone us-east-1a)
  ├─ Agent Instance 2 (edge2, availability zone us-east-1b)
  └─ Agent Instance 3 (edge3, availability zone us-east-1c)

User request → LB routes to instance with lowest latency
Result: 3× throughput, fault tolerant
```

**Load Balancing Strategy:**

```
Round-robin: distribute equally
  Pro: simple
  Con: ignores instance load

Least-loaded: route to least-busy instance
  Pro: load-aware
  Con: requires health checks

Latency-aware: route to fastest instance
  Pro: optimizes user experience
  Con: complex measurement

Sticky: keep user on same instance (if need local state)
  Pro: preserves local cache
  Con: uneven load
```

**Scaling Pattern:**

```
Metrics: latency_p99, request_rate, error_rate

Autoscale Rule:
- If latency_p99 > 500ms for 2 min → add instance
- If error_rate > 1% for 2 min → restart instances
- If request_rate < 10 RPS for 5 min → remove instance
```

## When to Use

- Replicate when single instance can't handle load
- Use least-loaded or latency-aware routing for user-facing agents
- Use round-robin for batch processing
- Implement autoscaling based on latency (not just CPU)

## References

- [Fair Queuing & Scheduling](../resource-allocation/fair-queuing.md)
- [Agent Health Metrics](../observability/agent-health-metrics.md)
