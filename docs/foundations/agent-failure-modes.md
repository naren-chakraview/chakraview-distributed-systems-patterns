# Agent-Specific Failure Modes

## Problem Statement

Agent systems fail differently than traditional distributed systems. Agents don't just timeout or crash — they degrade gracefully (or ungracefully). Context windows fill, tokens deplete, behavior diverges from expected. How do we recognize, predict, and recover from agent-specific failures?

## Solution Approach

**Key Failure Modes:**

1. **Non-determinism** — same input produces different output. Retrying doesn't replay identically; it consumes more tokens.
2. **Context degradation** — behavior changes as context window fills. Agent becomes less accurate, more verbose, or repetitive.
3. **Token depletion** — agent runs out of tokens mid-response. Incomplete output; corrupted state.
4. **Inference timeout** — cloud inference takes too long; edge times out before response arrives.
5. **Hallucination under pressure** — resource constraints trigger confabulation (agent makes up facts).
6. **Context thrashing** — agent repeatedly evicts and reloads context; high latency, inconsistent behavior.

**Observability Strategy:**

- Track actual vs budgeted tokens per turn
- Monitor latency percentiles (p99 > baseline = degradation signal)
- Check for repeated context compaction (sign of thrashing)
- Validate outputs against type/schema (detect hallucination)
- Sample model confidence (if available) — low confidence + unusual output = hallucination likely

## When to Use

Understand these failure modes when:
- Building reliability SLOs for agent workflows
- Debugging "sometimes works, sometimes doesn't" agent behavior
- Planning resource budgets (how much context to reserve?)
- Designing fallback strategies (which failures are recoverable?)

## Trade-offs

| Mode | Detectability | Recovery Difficulty | Frequency |
|------|---------------|-------------------|-----------|
| Non-determinism | Hard (need seeding/tracing) | Medium (replay with same seed) | High |
| Context degradation | Medium (latency spike) | Hard (need context compaction/recall) | Medium |
| Token depletion | Easy (check token count) | Hard (incomplete output, need retry) | Medium |
| Inference timeout | Easy (wall-clock timeout) | Medium (retry, reduce inference size) | Low-Medium |
| Hallucination | Hard (validation-dependent) | Medium (fallback, re-prompt) | Low-Medium |
| Context thrashing | Medium (log compactions) | Hard (restructure context) | Low |

## Observability Hooks

**Metrics:**
- Token budget burn rate (actual vs. expected)
- Latency percentiles (spike = degradation)
- Context compaction frequency
- Output validation failures
- Model confidence (if available)

**Queries:**
- "Which agent invocations exceeded token budget?"
- "When did this agent's latency spike?"
- "How often does this agent's output fail validation?"

## Example Failure Scenario

**Hallucination under context pressure:**
- Agent has 4K token context window, 2K already consumed by history
- Task requires complex reasoning; agent uses 1.5K tokens, leaving 500 remaining
- Insufficient space for full response; agent truncates and confabulates ending
- Output fails validation; workflow retries, consuming more tokens
- Eventually task fails or exhausts budget

**Prevention:** Reserve tokens upfront; check output validity before proceeding.

## References

- [Context Window Management](../patterns/predictability/context-window-management.md)
- [Token Budgeting](../patterns/predictability/token-budgeting.md)
- [Testing & Validation](../patterns/predictability/testing-and-validation.md)
