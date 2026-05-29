# Contributing

## Structure

This project is organized into layers:
1. **Foundations** — core concepts
2. **Patterns** — organized by problem area (observability, predictability, etc.)
3. **Case Study** — concrete example
4. **Examples** — code and demos

## Adding a Pattern

Patterns follow this structure:

```markdown
# [Pattern Name]

## Problem Statement
What challenge does this pattern solve?

## Solution Approach
How does the pattern work? Architecture/flow description.

## When to Use
When is this pattern applicable? When is it NOT?

## Trade-offs
What are the costs and benefits? Compared to what alternatives?

## Observability Hooks
How do you know if this pattern is working correctly? What metrics/logs should you monitor?

## Example
Code snippet or walkthrough showing the pattern in action.

## Failure Scenarios
What happens if this pattern breaks? Recovery strategies?

## References
- Related patterns
- Framework callouts (LangGraph, Crew, AutoGen, etc.)
- External resources
```

## Adding an Example

Code examples live in `examples/` organized by pattern area. Include:
- Clear comments explaining what the example demonstrates
- Runnable setup instructions
- Expected output

## Submitting Changes

1. Fork the repo
2. Create a feature branch: `git checkout -b patterns/my-pattern`
3. Add or modify files in `docs/`
4. Run `graphify update .` to update the knowledge graph (optional)
5. Commit with a clear message: `git commit -m "docs: add X pattern"`
6. Open a pull request

## Review Criteria

- Patterns are framework-agnostic (but may call out specific framework features)
- Patterns include observability strategies
- Patterns include failure scenarios
- Examples are concrete and runnable
- Language is clear and accessible to readers unfamiliar with agent systems
