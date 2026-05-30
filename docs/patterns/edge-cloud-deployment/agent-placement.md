# Agent Placement Strategy

## Problem Statement

Some agents run on edge devices (fast, local), others in cloud (powerful, shared). Where should a specific agent run? Edge has latency advantage but resource constraints. Cloud is powerful but high latency. How do we decide?

## Solution Approach

**Decision Factors:**

| Factor | Edge Advantage | Cloud Advantage |
|--------|---|---|
| **Latency** | <50ms (local) | 100-500ms (network) |
| **Model size** | 4-32K tokens (small) | 100K+ tokens (large) |
| **Inference cost** | Free (on-device) | $0.01-0.10/1K tokens |
| **Network bandwidth** | None (local) | Uses bandwidth |
| **Privacy** | Data stays on device | Data sent to cloud |
| **Complexity** | Simple tasks | Complex reasoning |

**Placement Rules:**

```
IF task is latency-critical (< 100ms)
  → Run on edge (accept smaller model, less powerful)
ELSE IF task is compute-intensive (complex reasoning)
  → Run on cloud (use large model)
ELSE IF task needs accuracy
  → Run on cloud (larger model = better accuracy)
ELSE IF data is private
  → Run on edge (keep data local)
ELSE
  → Default: run on cloud (fewer resource constraints)
```

**Example Placements:**

```
Latency-critical (user interaction):
  - Spelling correction → edge
  - Intent detection → edge
  - Latency budget < 500ms

Accuracy-critical (analysis):
  - Risk assessment → cloud
  - Fraud detection → cloud
  - Latency budget > 2s

Hybrid (best of both):
  - User input → edge (quick response)
  - Enrich with cloud analysis (async)
```

## When to Use

- Always consider edge for user-facing, latency-sensitive tasks
- Use cloud for complex, compute-intensive work
- Use hybrid for workflows where latency + quality matter

## Trade-offs

| Placement | Latency | Quality | Cost | Privacy |
|-----------|---------|---------|------|---------|
| **Edge** | Very low (<50ms) | Medium (small model) | Low | High (local) |
| **Cloud** | High (100-500ms) | Very high (large model) | High | Low (remote) |
| **Hybrid** | Low (edge) + medium (cloud) | High (best of both) | Medium | Medium |

**Recommendation:** Hybrid for edge+cloud systems: edge for latency, cloud for accuracy.

## References

- [Local vs. Remote Inference](inference-strategies.md)
- [Network Partition Handling](partition-handling.md)
