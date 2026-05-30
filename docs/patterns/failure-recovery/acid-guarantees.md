# ACID-like Guarantees for Agentic Workflows

## Problem Statement

Agents are unreliable (non-deterministic, may timeout or fail). How do we build reliable workflows where if one agent fails, the whole workflow doesn't lose consistency? How do we achieve ACID properties?

## Solution Approach

**ACID for Agents:**

- **Atomicity** — agent task either completes fully or not at all (no partial state)
- **Consistency** — invariants always held (e.g., "total == sum of parts")
- **Isolation** — concurrent agent tasks don't interfere
- **Durability** — if task commits, it survives failure

**Implementing via Sagas:**

Saga = sequence of agent tasks with compensations:

```
Task A (debit account) ✓
  → Task B (transfer to vendor) ✗ (vendor API down)
    → Compensate A (credit account back) ✓
  → Result: Account unchanged; transaction atomically fails
```

vs.

```
No saga:
  Account debited: -$100 ✓
  Vendor transfer failed ✗
  Account never credited back ✗ (money lost!)
```

**Implementation Pattern:**

```python
class AgentWorkflow:
    def execute_saga(self):
        tasks = [
            Task(action=debit_account, compensate=credit_account),
            Task(action=transfer_to_vendor, compensate=refund_vendor),
            Task(action=send_confirmation, compensate=revoke_confirmation),
        ]
        
        completed = []
        for task in tasks:
            try:
                task.execute()
                completed.append(task)
            except Exception:
                # Rollback all completed tasks
                for t in reversed(completed):
                    t.compensate()
                raise

result = workflow.execute_saga()  # All or nothing
```

**Consistency Invariants:**

```python
# Invariant: total_approved == sum of approvals
total_approved = 0
for agent in approval_agents:
    result = agent.run(task)
    if result.approved:
        total_approved += result.amount

assert total_approved == expected_total  # Consistency check
```

## When to Use

- Use for critical workflows: payments, approvals, contracts
- Skip for low-stakes: summaries, recommendations
- Use Sagas for workflows with external side effects (API calls, DB updates)

## Trade-offs

| Approach | Reliability | Complexity | Latency |
|----------|-----------|-----------|---------|
| **No guarantees** | Low | Low | Low |
| **Retry + idempotency** | Medium | Medium | Medium |
| **Saga pattern** | Very high | High | Medium (rollbacks) |
| **Saga + compensations** | Very high | Very high | Medium |

**Recommendation:** Use Saga for mission-critical; retry+idempotency for important.

## References

- [Idempotency & Replay](idempotency-and-replay.md)
- [Checkpointing Agent State](checkpointing.md)
- [Recovery Strategies](recovery-strategies.md)
