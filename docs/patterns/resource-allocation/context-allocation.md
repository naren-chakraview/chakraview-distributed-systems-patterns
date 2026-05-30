# Context Window Allocation Strategy

## Problem Statement

Context windows are limited resources. How do we allocate them fairly across agents and conversations?

## Solution Approach

**Static Allocation (Simple):**

All agents get equal context window:
```
Total context: 200K tokens (e.g., Claude model)
System prompt: 2K (reserved)
Available: 198K
Agent 1 gets: 198K / 4 agents = 49.5K
Agent 2 gets: 49.5K
... etc
```

**Dynamic Allocation (Fair):**

Allocate based on task complexity:
```
Simple task (summarization): 16K context
Medium task (analysis): 32K context
Complex task (reasoning): 64K context
Reserved (emergency): 20K

Total: 16+32+64+20 = 132K (leaves 68K unused for growth)
```

**Quota Allocation (User-Fair):**

Allocate per user/tenant:
```
User Alice: 50K tokens/hour
User Bob: 30K tokens/hour
User Carol: 20K tokens/hour
Total: 100K/hour reserved (if more needed, burst from shared pool)
```

**With Edge+Cloud:**

```
Edge agent context: 8K (small model, resource-constrained)
Cloud agent context: 32K (larger model, resource-rich)
```

## When to Use

- Use **static** for: homogeneous agents
- Use **dynamic** for: mixed task complexity
- Use **quota** for: multi-tenant systems
- Combine for: edge+cloud with quotas

## Trade-offs

| Approach | Fairness | Efficiency | Complexity |
|----------|----------|-----------|-----------|
| **Static** | High (equal) | Low (wastes capacity) | Low |
| **Dynamic** | Medium (complexity-based) | High (right-sized) | Medium |
| **Quota** | Very high (per-user fair) | Medium (must manage quotas) | High |

**Recommendation:** Use dynamic allocation; upgrade to quotas for multi-tenant.

## Example: Context Allocation Policy

```python
def allocate_context(task_type, model_capacity):
    # Total usable capacity
    usable = model_capacity - RESERVED_SYSTEM_PROMPT - RESERVED_OUTPUT
    
    allocation = {
        "simple": usable * 0.3,        # 30% for simple tasks
        "medium": usable * 0.5,        # 50% for medium
        "complex": usable * 0.8,       # 80% for complex
        "burst_pool": usable * 0.2     # 20% for emergency burst
    }
    
    return allocation[task_type]
```

## References

- [Token Budgeting](../predictability/token-budgeting.md)
- [Context Window Management](../predictability/context-window-management.md)
