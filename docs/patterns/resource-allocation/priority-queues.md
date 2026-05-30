# Priority Queues & Preemption

## Problem Statement

Some agent requests are more urgent: payment approvals vs recommendations. Should urgent requests wait in queue? Or should they preempt running work?

## Solution Approach

**Multi-Level Queues:**

```
Priority 0 (Critical): Payment, fraud alerts
  → immediate execution, preempt if needed
Priority 1 (Normal): Regular queries, API calls
  → standard queue, wait if needed
Priority 2 (Batch): Reports, bulk processing
  → background, execute when idle
```

**Preemption Strategy:**

- **Hard preemption** — stop running lower-priority job immediately
  - Risk: lower-priority job gets partial results, wasted computation
  - Benefit: urgent job runs immediately
  
- **Soft preemption** — finish current operation, then switch
  - Risk: small delay
  - Benefit: lower-priority job completes operation cleanly

- **No preemption** — never interrupt; queue urgent work
  - Risk: urgent requests wait
  - Benefit: no partial results; efficient

**Recommended: Soft preemption for edge+cloud**

```python
class PriorityScheduler:
    def schedule_task(self, task):
        if task.priority == CRITICAL:
            # Allow soft preemption
            if self.current_task and self.current_task.priority < CRITICAL:
                self.current_task.pause()  # soft preemption
                self.queues[task.priority].insert(task)
                return
        
        self.queues[task.priority].append(task)

    def run(self):
        while True:
            # Prioritize highest-priority available task
            task = None
            for priority in range(MAX_PRIORITY):
                if self.queues[priority]:
                    task = self.queues[priority].pop(0)
                    break
            
            if task:
                self.current_task = task
                result = execute(task)
                self.current_task = None
```

## When to Use

- Use multi-level queues for all systems (even if no preemption, structure helps)
- Use soft preemption for time-sensitive workflows
- Avoid hard preemption (dangerous for incomplete work)

## Trade-offs

| Approach | Urgency Response | Safety | Complexity |
|----------|-----------------|--------|-----------|
| **Single queue** | High latency for urgent | Safe | Very low |
| **Multi-queue no preemption** | Medium (still waits) | Safe | Low |
| **Multi-queue soft preemption** | Low latency (urgent runs soon) | Safe (clean pauses) | Medium |
| **Hard preemption** | Very low latency | Risky (partial results) | Medium |

**Recommendation:** Multi-level with soft preemption for edge+cloud.

## Observability Hooks

**Metrics:**
- Queue depth per priority
- Wait time per priority (should be low for critical)
- Preemption frequency (should be rare)

**Queries:**
- "How often is batch preempted?"
- "Average latency for priority 0 vs priority 2?"

## References

- [Fair Queuing & Scheduling](fair-queuing.md)
