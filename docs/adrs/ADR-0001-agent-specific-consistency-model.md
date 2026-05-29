# ADR-0001: Agent-Specific Consistency Model

**Date:** 2026-05-29  
**Status:** Accepted

## Problem

Traditional distributed systems consistency models (eventual, causal, strong) were designed for stateless or deterministically-updated state. Agent systems introduce non-determinism: the same agent invocation with the same input produces different outputs depending on model temperature, seed, and context.

How should we define consistency for agent state when the agent's own behavior is non-deterministic?

## Decision

Define **behavioral consistency** for agent state: the agent's behavior is predictable within defined bounds (token budget, latency bounds, quality metrics), even if outputs are not identical.

Separate concerns:
1. **State consistency** — shared context and conversation history must be eventually consistent across replicas
2. **Behavioral consistency** — agent behavior (token usage, latency, quality) must meet SLOs even with non-identical outputs

## Consequences

- Observability becomes critical: we must measure behavioral consistency, not output determinism
- SLOs must be probabilistic (p99 latency, expected token consumption)
- Failure recovery focuses on behavioral guarantees, not exact state replay
- Edge agents can use eventual consistency for context; behavioral guarantees are checked at coordination points
