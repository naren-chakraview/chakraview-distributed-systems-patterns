# Multi-Agent Coordination

## Problem Statement

Multiple specialized agents collaborate: one classifies, one analyzes, one decides. How do they coordinate? What if one fails? How do they handle conflicting results?

## Solution Approach

**Delegation Pattern:**

```
User Query
  ↓
Agent A (classifier)
  "This is a fraud case"
  ↓ delegates to
Agent B (fraud analyzer)
  "Risk score: 0.85"
  ↓ delegates to
Agent C (decision maker)
  "Escalate to human"
  ↓
Result
```

**Message Passing:**

```python
class AgentChain:
    def run(self, task):
        # A classifies
        classification = self.agent_a.run(task)
        
        # B analyzes (depends on A's result)
        analysis = self.agent_b.run({
            "task": task,
            "classification": classification
        })
        
        # C decides (depends on A + B)
        decision = self.agent_c.run({
            "task": task,
            "classification": classification,
            "analysis": analysis
        })
        
        return decision
```

**Handling Disagreement:**

```
If agents disagree (A says fraud, B says legitimate):
1. Check confidence scores
2. If tie: escalate to human
3. If one confident: use confident agent
4. Retry with different parameters
```

## When to Use

- Use when problem requires multiple specialists
- Use explicit delegation (not implicit; easier to debug)
- Use message passing (stateless communication)

## References

- [Distributed Tracing](../observability/distributed-tracing.md)
- [Recovery Strategies](../failure-recovery/recovery-strategies.md)
