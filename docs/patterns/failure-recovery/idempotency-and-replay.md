# Idempotency & Replay for Non-Deterministic Agents

## Problem Statement

Retrying an agent request is risky. Same input doesn't produce same output (non-determinism). Retrying consumes more tokens, may produce different answer, or fail differently. How do we safely retry agents?

## Solution Approach

**Idempotency Key Pattern:**

```
Request: user_id=alice, task_id=12345, retry=1
Idempotency Key: "user:alice:task:12345:retry:1"

On retry:
- Check if idempotency key was seen before
- If yes: return cached result (don't re-execute)
- If no: execute and cache result
```

**Deterministic Replay (if model supports):**

```python
# First attempt
result1 = model.generate(
    prompt="...",
    seed=12345,           # Fixed seed
    temperature=0.0       # Deterministic
)

# Retry with same seed → same output (if model deterministic)
result2 = model.generate(
    prompt="...",
    seed=12345,
    temperature=0.0
)

assert result1 == result2  # Guaranteed to be identical
```

**Detecting Genuine Divergence:**

```python
# If seed/temp same but outputs differ = model bug or non-determinism
result1 = agent.run(task, seed=12345)
result2 = agent.run(task, seed=12345)

if result1 != result2:
    # Model non-determinism detected
    # Safe to retry (both are valid answers)
    # Pick one or ask user
```

**Idempotency Storage:**

```json
{
  "idempotency_key": "user:alice:task:12345:retry:1",
  "timestamp": "2026-05-29T10:00:00Z",
  "request": { "task": "...", "context": "..." },
  "response": { "output": "...", "tokens": 145 },
  "ttl": 3600  // expire after 1 hour
}
```

## When to Use

- Always use idempotency keys for user-facing requests
- Use deterministic replay if model supports (seed + temperature=0)
- Store idempotency results for 1-24 hours (balance freshness vs storage)

## Trade-offs

| Approach | Safety | Efficiency | Complexity |
|----------|--------|-----------|-----------|
| **No idempotency** | Low (retries differ) | High (no storage) | Low |
| **Idempotency key only** | High (cached result) | Medium (stores results) | Low |
| **Deterministic seed** | Very high (identical) | Medium (may be slow) | Medium |
| **Both** | Very high | Medium | Medium |

**Recommendation:** Always use idempotency keys; upgrade to deterministic replay for critical paths.

## Observability Hooks

**Metrics:**
- Idempotency key hit rate (% of retries cached)
- Determinism validation (% where retry output matches first attempt)

**Queries:**
- "Show all retries for task X"
- "Which requests had divergent retry outcomes?"

## References

- [Checkpointing Agent State](checkpointing.md)
- [Recovery Strategies](recovery-strategies.md)
