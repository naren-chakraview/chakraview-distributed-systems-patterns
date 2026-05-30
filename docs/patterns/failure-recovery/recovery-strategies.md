# Recovery Strategies for Agent Failures

## Problem Statement

Agents fail: timeout, invalid output, exception, token depletion. What do we do? Retry? Fallback? Give up? Each failure mode needs a different recovery strategy.

## Solution Approach

**Recovery Strategies by Failure Type:**

| Failure | Root Cause | Recovery |
|---------|-----------|----------|
| **Timeout** | Inference too slow | Retry with reduced max_tokens; fallback to cached answer |
| **Invalid output** | Model hallucination | Retry with stricter validation; fallback to default |
| **Token depletion** | Context too large | Summarize history; retry; fallback |
| **Exception** | Bug in agent code | Retry (transient) or escalate (permanent) |
| **Low confidence** | Model uncertain | Retry; ask user for clarification; fallback |

**Retry Strategy:**

```python
@retry(
    max_attempts=3,
    backoff_factor=2,  # 1s, 2s, 4s
    on_exception=[TimeoutError, ValueError],
    on_condition=lambda r: r.confidence < 0.7
)
def run_agent_with_retry(task):
    return agent.run(task)
```

**Circuit Breaker (Prevent Cascading Failures):**

```
Normal: requests go through
    ↓ (after 5 errors in 1 minute)
Open: requests fail fast (don't try)
    ↓ (after 30 seconds)
Half-Open: test 1 request
    ↓ (if success)
Normal: resume
```

**Fallback Chain:**

```
Try: Complex reasoning
  ↓ (timeout)
Try: Simpler model
  ↓ (fails)
Try: Cached answer
  ↓ (no cache)
Try: Default answer ("I don't know")
  ✓ Return
```

## When to Use

- Use retry for transient failures (timeout, network error)
- Use circuit breaker to prevent cascade (e.g., if inference API down, fail fast)
- Use fallback for user-facing agents (never show error; show cached/default answer)
- Use escalation for critical workflows (payment failure → alert human)

## Trade-offs

| Strategy | Reliability | Latency | Cost |
|----------|------------|---------|------|
| **No recovery** | Low | Low | Low |
| **Retry only** | Medium | High (wait for retries) | Medium |
| **Circuit breaker** | High (prevents cascade) | Medium | Low |
| **Fallback chain** | Very high | Low (fallback fast) | High (run multiple) |

**Recommendation:** Retry for transient; circuit breaker for cascades; fallback for user-facing.

## Example: Payment Approval Recovery

```
Attempt 1: Run inference → Timeout
  → Retry with reduced tokens (1 attempt)
  
Attempt 2: Run inference → Invalid output (not yes/no)
  → Retry with stricter prompt (1 attempt)
  
Attempt 3: Run inference → Low confidence (0.6)
  → Fallback: Escalate to human approval
  
Result: Payment held for human review (safe but slower)
```

## References

- [Idempotency & Replay](idempotency-and-replay.md)
- [Checkpointing Agent State](checkpointing.md)
- [ACID-like Guarantees](acid-guarantees.md)
