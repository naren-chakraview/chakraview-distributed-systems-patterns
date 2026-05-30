# Testing & Validation for Agent Systems

## Problem Statement

Agents are non-deterministic. Same input produces different outputs. Traditional testing (assert output == expected) fails. How do we test agents?

## Solution Approach

**Validation Layers:**

1. **Type validation** — output is JSON, string, number (basic structure check)
2. **Schema validation** — output matches defined schema (fields, types, required)
3. **Quality validation** — output meets quality bar (no profanity, answer is relevant, etc.)
4. **Behavior validation** — agent behavior is consistent (two runs with same seed produce same output)
5. **Integration validation** — agent works with downstream systems (output parses as JSON, integrates with DB, etc.)

**Testing Pattern:**

```python
@test
def test_summarization_agent():
    # Type validation
    result = agent.run("summarize this document")
    assert isinstance(result, str)
    
    # Schema validation
    parsed = json.loads(result)
    assert "summary" in parsed
    assert isinstance(parsed["summary"], str)
    assert len(parsed["summary"]) < 500
    
    # Quality validation
    assert not contains_profanity(parsed["summary"])
    assert len(parsed["summary"]) > 50  # not empty
    assert "relevant_keywords" in parsed
    
    # Behavior validation (if seed exposed)
    result2 = agent.run("summarize this document", seed=12345)
    assert result2 == result  # deterministic with same seed
    
    # Integration validation
    vector = embedder.embed(parsed["summary"])
    assert len(vector) == 1536
```

**Production Validation:**

- Run quality checks on every invocation (async, non-blocking)
- Log validation failures (not errors; don't block user)
- Track quality metrics over time; alert on degradation

## When to Use

- Type + schema validation: always (reject invalid outputs)
- Quality validation: high-stakes (finance, content) or user-facing
- Behavior validation: debugging
- Integration validation: before deploying new downstream integrations

## Trade-offs

| Type | Cost | Strictness | False Positives |
|------|------|-----------|-----------------|
| **Type** | None (trivial) | Very low | None |
| **Schema** | Very low | Low | Rare |
| **Quality** | Medium (classifier) | High | Possible (false failures) |
| **Behavior** | High (recompute) | Perfect (deterministic) | None |
| **Integration** | Low | Medium | Rare |

**Recommendation:** Always do type + schema; add quality validation for critical paths; use behavior validation for debugging.

## Example

```python
def validate_agent_output(output, output_type="text"):
    """Validate agent output before using."""
    
    # Type check
    if output_type == "json":
        try:
            parsed = json.loads(output)
        except:
            return False, "Invalid JSON"
    
    # Length check
    if len(output) > 10000:
        return False, "Output too long"
    
    if len(output) < 10:
        return False, "Output too short"
    
    # Quality check (classifier-based)
    quality_score = quality_model.score(output)
    if quality_score < 0.7:
        return False, f"Low quality: {quality_score}"
    
    return True, "Valid"
```

## References

- [Agent Health Metrics](../observability/agent-health-metrics.md)
- [SLOs for Agentic Workloads](agentic-slos.md)
