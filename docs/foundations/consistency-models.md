# Consistency Models for Agent State

## Problem Statement

Agent systems maintain shared state: conversation history, tool results, decisions, context. Traditional consistency models assume deterministic state updates. But agents are non-deterministic — same input produces different outputs depending on temperature, seed, and context.

What does "consistency" mean for agent state when the agent's own behavior is probabilistic?

## Solution Approach: Behavioral Consistency

Define consistency in terms of agent **behavior**, not **state identity**:

- **Behavioral consistency**: agent behavior (latency, token usage, quality) remains predictable even if state replicas diverge
- **State consistency**: conversation history, tool results, execution logs eventually converge across replicas

**For Edge+Cloud Hybrid:**

| Scenario | Strategy |
|----------|----------|
| Edge agent reading conversation history | Eventual consistency (local cache + async sync with cloud) |
| Two edge agents coordinating | Causal consistency (one sends result, other reads in happened-before order) |
| Agent swarm aggregating results | Quorum consistency (wait for majority to report) |
| Workflow checkpointing | Strong consistency at boundaries (all agents agree state is saved) |

## When to Use

**Eventual consistency for:**
- Conversation history (delay acceptable)
- Observability logs (async sync ok)
- Metrics (freshness lag tolerable)

**Causal consistency for:**
- Coordinating results between agents
- Workflow steps (order matters)
- Multi-hop messages

**Strong consistency for:**
- Financial transactions
- Critical decisions with approval
- Checkpoint boundaries

## Trade-offs

| Model | Pros | Cons | Edge+Cloud |
|-------|------|------|-----------|
| **Eventual** | Fast; high availability | Stale reads; convergence delays | Good (local caching) |
| **Causal** | Respects causality | Overhead (vector clocks) | Good (agent messages ordered) |
| **Strong** | Simplest to reason about | Slow; fails on partition | Poor (can't coordinate across partition) |
| **Quorum** | Balances availability | Slower than eventual | Fair (quorum within edge, eventual edge-to-cloud) |

**Recommendation:** Use eventual as default; upgrade to causal when ordering matters; strong only at critical boundaries.

## Observability Hooks

**Metrics:**
- Replication lag (target: < 100ms edge; < 1s edge-to-cloud)
- Consistency violations (target: 0)
- Causal order violations (target: 0)

**Queries:**
- "What state did agent X see at time T?"
- "Did agents A and B see consistent data?"
- "How long to sync after partition healed?"

## Failure Scenarios

**State divergence:** Edge and cloud have different history.
- **Recovery:** Designate edge as primary; replay from edge; merge non-overlapping updates

**Causal order violation:** Agent B reads state A hasn't sent yet.
- **Recovery:** Vector clocks detect; reject stale reads

**Quorum disagreement:** Swarm reports conflicting results.
- **Recovery:** Force re-sync from authoritative quorum

## References

- [Causality & Ordering](causality-and-ordering.md)
- [Edge State Consistency](../patterns/edge-cloud-deployment/edge-state-consistency.md)
- Bailis, P., et al. (2013). "Highly Available Transactions"
