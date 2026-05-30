# Behavior Degradation Patterns

## Problem Statement

As context fills, agent behavior changes. Responses become shorter, less accurate, more repetitive. As latency budgets expire, agent produces incomplete output. How do we predict and handle graceful degradation?

## Solution Approach

**Degradation Signals:**

1. **Context window approaching limit** — agent has < 10% free context
2. **Latency budget consumed** — elapsed time > 80% of deadline
3. **Token budget exceeded** — actual tokens > expected
4. **Quality metrics dropping** — confidence scores declining, validation failures increasing
5. **Output truncation** — response was cut off mid-sentence

**Graceful Degradation:**

```
Normal Flow:
user_query → (2s latency budget)
  ├─ gather context (0.5s)
  ├─ run inference (1.2s)
  └─ format response (0.3s)
  ✓ Complete response in 2.0s

Degraded Flow (approaching deadline):
user_query → (2s latency budget, 1.8s elapsed)
  ├─ skip context gathering (too late)
  ├─ use cached context (0.1s)
  ├─ run quick inference (minimal output) (0.8s)
  └─ return abbreviated response
  ⚠ Partial response in 1.9s (still meets deadline, less complete)
```

**Strategies:**

1. **Progressive compression** — as context fills, summarize older turns
2. **Quality degradation** — accept lower-quality output rather than fail
3. **Latency-aware inference** — reduce max_tokens as deadline approaches
4. **Fallback chain** — if full inference times out, use cached response or default answer

## When to Use

- Monitor degradation signals in all production agents
- Implement graceful degradation for user-facing agents (better partial answer than timeout)
- Use for resource-constrained deployments (edge devices)

## Trade-offs

| Approach | Latency | Quality | UX Impact |
|----------|---------|---------|-----------|
| **Fail fast** | Low | None | Bad (error) |
| **Progressive compression** | Medium | Good | Ok (slightly slower, same quality) |
| **Quality reduction** | Medium | Reduced | Medium (less complete answer) |
| **Fallback chain** | Low | Lower | Medium (cached answer may be stale) |

**Recommendation:** Graceful degradation with quality monitoring; alert when degrading below threshold.

## Observability Hooks

**Metrics:**
- Degradation event frequency (how often?)
- Quality delta when degraded (how much worse?)
- Fallback activation rate

**Queries:**
- "When did this agent degrade?"
- "How much did quality drop compared to normal?"

## Code References

### Reference Implementation

**Degradation Implementation:**
- File: `reference-implementations/edge_agents/intent_agent.py`
- Method: `_degrade_to_keyword_matching()` (lines 201-252)
  - Triggers when token budget exceeded
  - Falls back to keyword matching
  - Reduces confidence scores (max 0.6 in degraded mode)
  - Uses minimal tokens (1/20 of normal estimate)

**Budget-Triggered Degradation:**
- Lines 144-149: Budget check triggers degradation path
- Line 223: `degraded_tokens = max(1, len(message) // 20)` — minimal token allocation in degraded mode

**Confidence Reduction:**
- Line 229: `confidence = min(0.6, best_intent[1] * 0.7)` — explicitly cap degraded confidence

### Tests

**Integration Tests:**
- File: `tests/integration/test_full_pipeline.py`
- Test: `test_degradation_mode_behavior()` (lines 250-275)
  - Exhausts token budget
  - Verifies agent still produces results
  - Validates graceful fallback behavior

**Fixtures:**
- File: `tests/conftest.py`
- MockIntentAgent: Simulates degradation path
- Test setup allows budget constraint testing

### Demo Scripts

- File: `examples/pattern-demos/demo_token_budgeting.py`
  - Shows degradation in action
  - Demonstrates confidence score changes
  - Illustrates token savings from degradation

## References

- [Context Window Management](context-window-management.md)
- [Token Budgeting](token-budgeting.md)
- [SLOs for Agentic Workloads](agentic-slos.md)
- [Understanding Model Decisions](../observability/understanding-decisions.md)
