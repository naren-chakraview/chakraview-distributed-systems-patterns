# Fair Queuing & Scheduling for Agent Workloads

## Problem Statement

Multiple agents compete for resources: GPU, inference API, memory. Without fair scheduling, some agents starve while others hog resources. How do we fairly allocate resources?

## Solution Approach

**Scheduling Strategies:**

1. **FIFO (First-In-First-Out)** — simplest; first agent to arrive executes first
   - Fair? No (early arriving agent starves)
   - Latency? High variance (depends on queue depth)

2. **Weighted Fair Queuing (WFQ)** — allocate resources proportional to weight
   - Edge agents get 30%, cloud agents get 50%, batch agents get 20%
   - Fair? Yes (each gets fair share of bandwidth)
   - Latency? Medium (some queueing)

3. **Strict Priority** — critical agents jump queue
   - Critical (payment): priority 0 (execute immediately)
   - Normal: priority 1
   - Batch: priority 2
   - Fair? No (low-priority starves)
   - Latency? Low for critical, high for batch

4. **Deficit Round Robin (DRR)** — hybrid approach
   - Each agent gets turn (round-robin)
   - Within turn, agent uses allocated budget (bytes/tokens)
   - Fair? Better than FIFO
   - Latency? Medium

**Implementation Pattern:**

```python
class FairScheduler:
    def __init__(self):
        self.queues = {
            "critical": [],
            "normal": [],
            "batch": []
        }
        self.weights = {
            "critical": 0.5,
            "normal": 0.3,
            "batch": 0.2
        }
    
    def schedule(self):
        # Round-robin across priority levels
        for priority in ["critical", "normal", "batch"]:
            if self.queues[priority]:
                job = self.queues[priority].pop(0)
                budget = self.weights[priority] * TOTAL_BUDGET
                yield job, budget
```

## When to Use

- Use FIFO for homogeneous workloads (all agents similar)
- Use WFQ for mixed workloads (different agent types)
- Use strict priority for critical vs batch
- Use DRR for fine-grained fairness

## Trade-offs

| Strategy | Fairness | Simplicity | Latency for Critical |
|----------|----------|-----------|----------------------|
| **FIFO** | Low | High | High (may queue) |
| **WFQ** | High | Medium | Medium (proportional) |
| **Strict Priority** | Low (starves low-priority) | Medium | Low (skips queue) |
| **DRR** | Very High | Low | Low |

**Recommendation:** Use WFQ for edge+cloud hybrid (30% edge, 70% cloud); use strict priority for critical workflows.

## Observability Hooks

**Metrics:**
- Queue depth per priority
- Wait time per priority
- Resource utilization per agent pool
- Starvation events (batch never runs)

**Queries:**
- "Which agents are waiting in queue?"
- "Average wait time per priority level?"

## References

- [Priority Queues & Preemption](priority-queues.md)
- [Token Budgeting](../predictability/token-budgeting.md)
