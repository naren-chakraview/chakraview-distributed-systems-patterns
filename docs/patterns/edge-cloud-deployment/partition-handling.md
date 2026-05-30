# Network Partition Handling

## Problem Statement

Edge agents communicate with cloud over the network. Networks are unreliable: drops, latency spikes, partitions. When edge-cloud connection fails, what happens? Do edge agents continue? Do they wait? How do they reconnect?

## Solution Approach

**Detection:**

```
Normal: edge sends request, cloud responds within 1s
Slow: edge sends request, cloud takes > 5s
Down: edge sends request, no response after 30s

Detection:
- After 3 consecutive timeouts → partition suspected
- Mark all cloud agents as "unavailable"
```

**While Partitioned (Edge Isolated):**

```
Strategy 1: Fail requests
  - Return error "Cloud unavailable"
  - Pro: honest
  - Con: service degradation

Strategy 2: Local fallback
  - Use cached cloud responses
  - Use edge model (smaller, faster)
  - Pro: service continues
  - Con: stale/lower-quality answers

Strategy 3: Queue for later
  - Queue requests locally
  - When partition heals, flush queue
  - Pro: no lost requests
  - Con: may exceed edge storage
```

**Reconnection (Healing):**

```
Partition healed → cloud responds again
  ├─ Replay queued requests (if Strategy 3)
  ├─ Verify cached results still valid (TTL check)
  ├─ Re-sync state (consistent?)
  └─ Resume normal operation
```

**Reconciliation (State Sync):**

```
Edge state during partition:
  - Turn 10: user query (processed locally)
  - Turn 11: agent response (using cache)
  - Turn 12: user query (queued, not processed)

Cloud state (doesn't know about partition):
  - Turns 1-9: synced

Reconciliation:
  - Merge edge + cloud state
  - Detect conflicts (edge turn 10 vs cloud different?)
  - Use vector clocks: if edge turn 10 > cloud turn 9 = edge wins
  - Replay merged state to cloud
```

## When to Use

- Always implement partition detection (health checks every 5-10s)
- Use local fallback for user-facing agents
- Use queue + replay for critical workflows
- Implement state reconciliation for long conversations

## Trade-offs

| Strategy | Service Continuity | Data Loss Risk | Complexity |
|----------|------------------|----------------|-----------|
| **Fail fast** | Low (errors) | None | Low |
| **Local fallback** | High (continues) | Low (stale data) | Medium |
| **Queue** | High (continues) | None (replayed) | High |
| **All three** | Very high | None | Very high |

**Recommendation:** Partition detection + local fallback + eventual queue flush.

## References

- [Asynchronous Coordination](async-coordination.md)
- [Edge State Consistency](edge-state-consistency.md)
