# Local vs. Remote Inference

## Problem Statement

Run inference on edge or cloud? Each has tradeoffs.

**Edge inference:**
- Pro: fast (<50ms), no network latency, privacy
- Con: small models, limited capability, high resource cost per device

**Cloud inference:**
- Pro: large models, high capability, cheaper per request
- Con: network latency (100-500ms), privacy concerns

**Hybrid:**
- Edge: fast local processing
- Cloud: powerful models
- Combine results

## Solution Approach

**Local Inference (Edge):**

```
Constraints: 4K-32K tokens, 100-1000 tokens/sec
Use: Fast tasks that don't need complex reasoning
Examples: intent detection, spelling, sentiment

Model: small (7B-13B params)
Latency: <100ms
Quality: Medium (smaller model)
```

**Remote Inference (Cloud):**

```
Capacity: 100K+ tokens, 10K+ tokens/sec
Use: Complex reasoning, accuracy-critical
Examples: analysis, summarization, planning

Model: large (50B+ params)
Latency: 500-2000ms (network + compute)
Quality: High (larger model)
```

**Hybrid (Cascade):**

```
Edge: Quick classification/filtering
  ↓ (if simple, respond; else forward)
Cloud: Complex analysis
  ↓ (if confident, respond; else escalate)
Human: Review if needed
```

## When to Use

- Use edge for latency-critical, simple tasks
- Use cloud for accuracy-critical, complex tasks
- Use hybrid for workflows needing both

## Trade-offs

| Strategy | Latency | Quality | Cost |
|----------|---------|---------|------|
| **Edge** | <100ms | Medium | Low |
| **Cloud** | 500-2000ms | High | High |
| **Hybrid** | Medium | High | Medium |

## References

- [Agent Placement](agent-placement.md)
- [Context Window Management](../predictability/context-window-management.md)
