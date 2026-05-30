# Checkpointing Agent State

## Problem Statement

Long-running agent workflows can fail halfway through. If an agent completes 10 turns of a 20-turn conversation, losing those 10 turns is expensive (tokens wasted, user confused). How do we save and recover agent state?

## Solution Approach

**Checkpoint What:**

1. **Conversation history** — every user message and agent response
2. **Intermediate results** — tool outputs, computed values
3. **Agent decisions** — key choices made (e.g., "decided to escalate")
4. **Metadata** — timestamps, vector clocks, trace IDs

**Checkpoint When:**

- **Every N turns** (e.g., every 5 turns)
- **After critical decisions** (payment approved, decision threshold crossed)
- **Before risky operations** (calling external API, state mutation)
- **On timeout** (save partial progress before giving up)

**Checkpoint Storage:**

```json
{
  "checkpoint_id": "conv:alice:12345:turn:15",
  "timestamp": "2026-05-29T10:15:00Z",
  "turn": 15,
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    // ... 14 more turns
  ],
  "agent_state": {
    "decision_log": ["forward_to_cloud", "request_approval"],
    "context_used": 5432,
    "budget_remaining": 1568
  },
  "recovery_metadata": {
    "can_restart_from": true,
    "resumption_point": "waiting_for_user_input"
  }
}
```

**Recovery from Checkpoint:**

```
Failure at turn 17 → restore checkpoint from turn 15
  ├─ Load conversation history (15 turns)
  ├─ Restore agent state (decision log, budget)
  ├─ Resume from "waiting_for_user_input"
  └─ Continue normally (turns 16, 17, ...)
  
Cost: ~30 tokens (reload history) vs ~5000 tokens (restart from turn 1)
```

## When to Use

- Checkpoint every critical workflow (payment, approval)
- Checkpoint long conversations (> 10 turns)
- Checkpoint before external API calls
- Don't checkpoint trivial queries (one-shot answers)

## Trade-offs

| Frequency | Recovery Speed | Storage Cost | Complexity |
|-----------|----------------|--------------|-----------|
| **Every turn** | Instant | High (too much storage) | High |
| **Every 5 turns** | Very fast (5 turns lost) | Medium | Medium |
| **Every 10 turns** | Fast (10 turns lost) | Low | Low |
| **Manual (critical points)** | Depends | Low | Medium |

**Recommendation:** Every 5 turns for conversational agents; every critical decision for workflows.

## References

- [Idempotency & Replay](idempotency-and-replay.md)
- [Recovery Strategies](recovery-strategies.md)
