# Edge State Consistency

## Problem Statement

Edge agents have local context; cloud agents have remote context. How do we keep them consistent when they diverge? When should state be shared vs local?

## Solution Approach

**State Classification:**

| Type | Location | Sync Strategy |
|------|----------|---|
| **Conversation history** | Edge (primary) + Cloud (backup) | Async sync every 5 turns |
| **User profile** | Cloud (primary) | Fetch on-demand, cache for 1 hour |
| **Intermediate results** | Edge (temporary) | Sync after decision |
| **Decisions** | Both (immutable log) | Sync immediately |

**Sync Strategies:**

1. **Eventual consistency** — history eventually syncs, delays acceptable
   - Use: conversation history
   - Policy: sync every N turns or on timeout

2. **Causal consistency** — one agent sends result, other receives before processing
   - Use: decision dependencies (B depends on A's result)
   - Policy: explicit acknowledgment required

3. **Strong consistency** — all agents see same state immediately
   - Use: financial transactions, critical decisions
   - Policy: two-phase commit or quorum

**Implementation (Eventual Consistency Example):**

```python
# Edge agent
conversation = [turn1, turn2, ...]
checkpoint_id = "conv:alice:12345:turn:10"
queue.send("sync_checkpoint", {
  "checkpoint_id": checkpoint_id,
  "history": conversation,
  "timestamp": time.time()
})

# Cloud agent (async)
checkpoint = queue.recv("sync_checkpoint", timeout=60s)
if checkpoint:
  # Update cloud history if newer
  if checkpoint.timestamp > cloud_history.timestamp:
    cloud_history = checkpoint.history
```

## When to Use

- Use eventual consistency for conversation history (delays acceptable)
- Use causal consistency for decision dependencies
- Use strong consistency for critical transactions (payments)

## Trade-offs

| Model | Consistency | Latency | Complexity |
|-------|-------------|---------|-----------|
| **Eventual** | Weak (lags) | Low (no wait) | Low |
| **Causal** | Strong (ordered) | Medium (wait for ack) | Medium |
| **Strong** | Perfect | High (blocking) | High |

**Recommendation:** Eventual for history; causal for decisions; strong for payments.

## References

- [Consistency Models](../../foundations/consistency-models.md)
- [Network Partition Handling](partition-handling.md)
