# Context Window Management

## Problem Statement

Context windows are finite: Claude 3.5 Sonnet has 200K tokens; edge models have 4K-32K. As conversation grows, context fills. What happens then? Does the agent truncate? Compress? Forget? How does available context affect agent behavior?

Managing context windows is critical for predictability.

## Solution Approach

**Context Layers (in order of priority):**

1. **System prompt** (reserved, never removed) — model instructions, behavior rules
2. **Recent messages** (high priority) — last N turns; usually recent context is most relevant
3. **Retrieved context** (medium priority) — search results, tool outputs, facts
4. **Conversation history** (low priority) — older turns; can be summarized or removed

**Strategies:**

1. **Sliding window** — keep last N tokens; discard older messages when full
2. **Summarization** — periodically summarize old context into bullet points; replace with summary
3. **Relevance filtering** — use embeddings to keep most-relevant context; discard irrelevant
4. **Hierarchical context** — store context in tiers: immediate (recent), intermediate (last day), archived (older); fetch as needed

**Monitoring:**

```json
{
  "total_window": 200000,
  "reserved_system": 2000,
  "reserved_response": 5000,
  "available_context": 193000,
  "used_context": 145000,
  "free_context": 48000,
  "context_utilization": 0.75,
  "turns_since_summarization": 12,
  "predicted_overflow_in_turns": 8
}
```

## When to Use

- Always track available context (reserve system prompt + response buffer)
- Use sliding window for streaming (simplest)
- Use summarization for long conversations (preserve more history)
- Use relevance filtering for multi-query workflows
- Use hierarchical context for very large contexts (100K+ tokens)

## Trade-offs

| Strategy | Simplicity | History Preservation | Latency | Cost |
|----------|-----------|----------------------|---------|------|
| **Sliding Window** | High (trivial) | Low (old context lost) | Low | Low |
| **Summarization** | Medium (need summarizer) | High (summary + recent) | Medium (summarization cost) | Medium |
| **Relevance Filtering** | Medium (embeddings needed) | Medium (keeps relevant) | Medium (search cost) | Medium |
| **Hierarchical** | Low (complex) | High (all available) | Low (only fetch needed) | Medium |

**Recommendation:** Start with sliding window; upgrade to summarization for multi-turn.

## Observability Hooks

**Metrics:**
- Context utilization (% of window used)
- Summarizations per conversation (how often contexts compress?)
- Predicted overflow (turns until capacity exhausted)

**Queries:**
- "Which conversations hit context limit?"
- "How much history is preserved after summarization?"

## References

- [Token Budgeting](token-budgeting.md)
- [Behavior Degradation](behavior-degradation.md)
