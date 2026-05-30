# Asynchronous Coordination

## Problem Statement

Edge agents can't always wait for cloud responses (too slow). Cloud agents can't always push to edge immediately (network full). How do we coordinate asynchronously?

## Solution Approach

**Message Queue Pattern:**

```
Edge Agent:
  task = {user_input: "...", priority: "normal"}
  queue.send("cloud_tasks", task)
  // Don't wait for response; continue

Cloud Agent:
  task = queue.recv("cloud_tasks")
  result = {output: "...", status: "success"}
  queue.send("edge_results", result)

Edge Agent (later):
  result = queue.recv("edge_results", timeout=5s)
  return result to user
```

**Async Patterns:**

1. **Fire-and-forget** — edge doesn't wait for response
   - Use: non-critical operations (logging, analytics)
   
2. **Request-response with timeout** — edge waits with timeout
   - Use: normal operations
   
3. **Batch aggregation** — accumulate edge requests, send in batch
   - Use: high volume, batch-able work

**Ordering Guarantees:**

```
Without ordering:
  Edge sends: Request A, Request B
  Cloud receives: Request B, Request A (out of order)
  Result: B processed before A; wrong!

With ordering (partition key):
  Request A: partition_key = "user:alice"
  Request B: partition_key = "user:alice"
  Queue guarantees: A then B (same partition)
```

## When to Use

- Use async for high-latency edge-cloud connections
- Use fire-and-forget for non-critical work
- Use request-response for interactive workflows
- Use batch for high-volume work

## Trade-offs

| Pattern | Latency | Ordering | Complexity |
|---------|---------|----------|-----------|
| **Fire-and-forget** | Low (no wait) | None (async) | Low |
| **Request-response** | High (wait) | Per-key (partition) | Medium |
| **Batch** | Medium (batch delay) | Per-batch | High |

**Recommendation:** Request-response with timeout for interactive; batch for analytics.

## References

- [Network Partition Handling](partition-handling.md)
- [Asynchronous Coordination](async-coordination.md)
