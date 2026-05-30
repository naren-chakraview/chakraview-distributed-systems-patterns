# Token Budgeting

## Problem Statement

Tokens are the currency of agent systems. Each token costs money and latency. Without budgeting, costs explode and latency becomes unpredictable. How do we budget tokens reliably?

## Solution Approach

**Budget Structure (for a single agent invocation):**

```
Total Budget: 4000 tokens
├─ System Prompt: 500 (reserved, never removed)
├─ User Input: 200 (actual)
├─ Context / History: 800 (allocated, may be less actual)
├─ Tool Outputs: 200 (placeholder for tool results)
├─ Reserved for Output: 500 (reserved)
└─ Flexible Buffer: 800 (available for additional context if input is shorter)

Total Allocated: 3600
Free: 400 (emergency buffer for unexpected growth)
```

**Budget Rules:**

1. **Reserve system prompt** — always allocate; never remove
2. **Reserve output buffer** — allocate expected output size + margin (expected 300, reserve 500)
3. **Estimate input tokens** — use actual token count; don't guess
4. **Allocate context dynamically** — if input < expected, use freed tokens for more context
5. **Never exceed total** — fail fast if would exceed; don't attempt

**Monitoring:**

```python
budget = TokenBudget(total=4000)
budget.reserve("system_prompt", 500)
budget.reserve("output", 500)

actual_input = tokenize(user_query)  # 150 tokens
budget.allocate("input", actual_input)

freed = budget.freed()  # 50 tokens (200 - 150)
budget.allocate("context", min(freed + 800, available_context))

if budget.remaining() < 100:
    raise BudgetExhausted("Insufficient buffer for safety")
```

## When to Use

- Implement token budgeting for all agent invocations
- Track budget vs actual; alert on overage
- Use for cost control + predictability

## Trade-offs

| Approach | Accuracy | Flexibility | Complexity |
|----------|----------|-------------|-----------|
| **Fixed allocation** | Low (ignores actual) | Low (rigid) | Low |
| **Dynamic allocation** | High (actual-based) | High (adapts) | Medium |
| **Per-agent budgets** | Medium | Medium | Medium |
| **Per-user quotas** | High (limits users) | Low | High |

**Recommendation:** Dynamic allocation per invocation; aggregate to user quotas for fairness.

## Observability Hooks

**Metrics:**
- Budget utilization (actual / allocated)
- Budget overage events (attempted > total)
- Cost per invocation
- Cost per user

**Queries:**
- "Which users are heaviest token consumers?"
- "Invocations that exceeded budget"

## Code References

### Reference Implementation

**Agent Base Class:**
- File: `reference-implementations/shared/python/agent_base.py`
- Lines: 19-40 (AgentConfig with token_budget)
- Method: `execute()` (lines 82-131) - budget checking and enforcement

**Edge Agents:**
- Intent Detection: `reference-implementations/edge_agents/intent_agent.py`
  - Token estimation: Line 140 (`tokens_estimate = max(1, len(message) // 4)`)
  - Budget checking: Lines 144-149
  - Token tracking: Line 184 (`self.token_usage`)
- Fraud Detection: `reference-implementations/edge_agents/fraud_agent.py`
  - Similar pattern to intent detection

**Cloud Agents:**
- Trends Analysis: `reference-implementations/cloud_agents/trends_agent.py`
  - Higher token budgets (10000 vs 5000 for edge)

### Tests

**Integration Tests:**
- File: `tests/integration/test_full_pipeline.py`
- Test: `test_token_budgeting_across_agents()` (lines 150-180)
  - Verifies token consumption across multiple agent invocations
  - Validates budget enforcement
  - Checks budget remaining calculation

**Test Fixtures:**
- File: `tests/conftest.py`
  - AgentConfig class: Lines 30-40
  - MockIntentAgent: Lines 64-95 (token_usage tracking)
  - Fixture definitions: Lines 200+ (agent configs with budgets)

### Demo Scripts

- File: `examples/pattern-demos/demo_token_budgeting.py`
  - Live demonstration of budget exhaustion
  - Shows token estimation accuracy
  - Demonstrates degradation mode

## References

- [Context Window Management](context-window-management.md)
- [Resource Allocation Strategy](../resource-allocation/reservation-vs-burst.md)
- [Behavior Degradation](behavior-degradation.md)
