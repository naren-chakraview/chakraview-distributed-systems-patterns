# Distributed Systems for Agentic Workloads — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Each task builds independently and produces a testable, committable increment.

**Goal:** Document distributed systems patterns and practices for LLM-backed agents deployed in edge+cloud hybrid environments, covering observability, predictability, resource allocation, and failure recovery.

**Architecture:** 5-layer organization (Foundations → Core Patterns → Deployment Patterns → Integration Patterns → Case Study), each layer building on prior ones. Framework-agnostic patterns with concrete examples and code.

**Tech Stack:** Markdown documentation, Python/TypeScript/Go code examples, Mermaid diagrams, optional runnable demos.

---

## Phase 1: Foundations & Observability (Layers 1-2.1)

**Deliverable:** Readers understand foundational concepts and can observe agent behavior in production.

**Estimated effort:** 2-3 weeks (8-10 tasks)

### Task 1: Initialize Documentation Structure & README

**Files:**
- Create: `README.md`
- Create: `docs/index.md`
- Create: `CONTRIBUTING.md`
- Create: `.gitignore`

**Steps:**

- [ ] **Step 1: Write project README**

Create `README.md`:

```markdown
# chakraview-distributed-systems-patterns

Distributed systems patterns and practices for LLM-backed agent systems deployed in edge+cloud hybrid environments.

This project documents patterns for **observability**, **predictability**, **resource allocation**, and **failure recovery** in agentic systems — challenges that emerge when agents are distributed across networks.

## Quick Start

- **New to agent systems?** Start with [Foundations](docs/foundations/)
- **Want to observe agents?** See [Observability Patterns](docs/patterns/observability/)
- **Debugging a failure?** Check [Failure Recovery Patterns](docs/patterns/failure-recovery/)
- **Deploying at scale?** Read [Deployment Patterns](docs/patterns/edge-cloud-deployment/)
- **See it all together?** Read the [Case Study](docs/case-study/)

## Contents

- **[Foundations](docs/foundations/)** — Core concepts (causality, consistency, failure modes, time, trust)
- **[Patterns](docs/patterns/)** — Observability, Predictability, Resource Allocation, Failure Recovery, Edge+Cloud Deployment, Integration
- **[Case Study](docs/case-study/)** — Large-scale analytics engine demonstrating patterns in practice
- **[Examples](examples/)** — Code snippets and runnable demos
- **[ADRs](docs/adrs/)** — Architecture Decision Records

## About This Project

This is one of six portfolio projects exploring architecture at scale. See [Chakraview Portfolio](https://naren-chakraview.github.io/) for related work on enterprise modernization, real-time data platforms, and data engineering patterns.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add patterns, examples, or feedback.
```

- [ ] **Step 2: Write docs/index.md (table of contents)**

Create `docs/index.md`:

```markdown
# Distributed Systems for Agentic Workloads — Documentation Index

## Navigation

### [Foundations](foundations/)
Core distributed systems concepts adapted for agent systems.

- [Causality & Ordering](foundations/causality-and-ordering.md) — Happens-before relations, vector clocks
- [Consistency Models](foundations/consistency-models.md) — Eventual, causal, and strong consistency for agent state
- [Agent Failure Modes](foundations/agent-failure-modes.md) — Non-determinism, context degradation, token depletion
- [Time, Clocks & Synchronization](foundations/time-and-clocks.md) — Clock skew, event-time, timeout detection
- [Trust & Byzantine Agents](foundations/trust-and-byzantine.md) — Verifying agent claims, consensus with untrusted agents

### [Patterns](patterns/)

#### [Observability](patterns/observability/)
Making agent systems transparent and debuggable.

- [Distributed Tracing](patterns/observability/distributed-tracing.md)
- [Understanding Model Decisions](patterns/observability/understanding-decisions.md)
- [Logging Strategies](patterns/observability/logging-strategies.md)
- [Agent Health Metrics](patterns/observability/agent-health-metrics.md)

#### [Predictability](patterns/predictability/)
Making agent behavior forecastable.

- [Context Window Management](patterns/predictability/context-window-management.md)
- [Behavior Degradation Patterns](patterns/predictability/behavior-degradation.md)
- [Token Budgeting](patterns/predictability/token-budgeting.md)
- [Testing & Validation](patterns/predictability/testing-and-validation.md)
- [SLOs for Agentic Workloads](patterns/predictability/agentic-slos.md)

#### [Resource Allocation](patterns/resource-allocation/)
Fair scheduling and resource management.

- [Fair Queuing & Scheduling](patterns/resource-allocation/fair-queuing.md)
- [Reservation vs. Burst](patterns/resource-allocation/reservation-vs-burst.md)
- [Context Window Allocation](patterns/resource-allocation/context-allocation.md)
- [Priority Queues & Preemption](patterns/resource-allocation/priority-queues.md)

#### [Failure Recovery](patterns/failure-recovery/)
Transactional guarantees for agentic workflows.

- [Idempotency & Replay](patterns/failure-recovery/idempotency-and-replay.md)
- [Checkpointing Agent State](patterns/failure-recovery/checkpointing.md)
- [Recovery Strategies](patterns/failure-recovery/recovery-strategies.md)
- [ACID-like Guarantees](patterns/failure-recovery/acid-guarantees.md)

#### [Edge+Cloud Deployment](patterns/edge-cloud-deployment/)
Patterns specific to distributed agent topologies.

- [Agent Placement](patterns/edge-cloud-deployment/agent-placement.md)
- [Network Partition Handling](patterns/edge-cloud-deployment/partition-handling.md)
- [Asynchronous Coordination](patterns/edge-cloud-deployment/async-coordination.md)
- [Local vs. Remote Inference](patterns/edge-cloud-deployment/inference-strategies.md)
- [Edge State Consistency](patterns/edge-cloud-deployment/edge-state-consistency.md)

#### [Integration Patterns](patterns/integration/)
Scaling agents and coordinating workflows.

- [Single-Agent at Scale](patterns/integration/single-agent-scale.md)
- [Multi-Agent Coordination](patterns/integration/multi-agent-coordination.md)
- [Agent Swarms](patterns/integration/agent-swarms.md)
- [Hierarchical Agent Networks](patterns/integration/hierarchical-networks.md)

### [Case Study](case-study/)
Large-scale AI analytics engine demonstrating all patterns.

- [Scenario Overview](case-study/scenario-overview.md)
- [Architecture](case-study/architecture.md)
- [Pattern Application](case-study/pattern-application.md)

### [Examples](../examples/)
Code snippets, configurations, and runnable demos.

### [Architecture Decision Records](adrs/)
Design decisions and their rationale.
```

- [ ] **Step 3: Write CONTRIBUTING.md**

Create `CONTRIBUTING.md`:

```markdown
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
```

- [ ] **Step 4: Create directory structure**

Run:
```bash
mkdir -p docs/foundations
mkdir -p docs/patterns/observability
mkdir -p docs/patterns/predictability
mkdir -p docs/patterns/resource-allocation
mkdir -p docs/patterns/failure-recovery
mkdir -p docs/patterns/edge-cloud-deployment
mkdir -p docs/patterns/integration
mkdir -p docs/case-study
mkdir -p docs/adrs
mkdir -p examples/observability
mkdir -p examples/predictability
mkdir -p examples/resource-allocation
mkdir -p examples/failure-recovery
mkdir -p reference-implementations
```

- [ ] **Step 5: Create empty placeholder files for all pattern documents**

For each pattern listed in `docs/index.md`, create an empty file with a frontmatter header:

Example — create `docs/foundations/causality-and-ordering.md`:

```markdown
# Causality & Ordering in Agent Networks

> Status: In Progress

## Problem Statement

TBD

## Solution Approach

TBD

## References

- Related patterns: (list)
- Frameworks: (LangGraph features, etc.)
```

Repeat for all 29 pattern files listed in `docs/index.md`.

- [ ] **Step 6: Create ADR template and first ADR**

Create `docs/adrs/README.md`:

```markdown
# Architecture Decision Records

This directory contains architectural decisions for the project.

## Format

We use MADR (Markdown Architectural Decision Records):

```markdown
# ADR-NNNN: [Title]

**Date:** YYYY-MM-DD  
**Status:** Accepted | Proposed | Deprecated

## Problem

Context and problem statement.

## Decision

Decision and rationale.

## Consequences

What follows from this decision?
```

## Decisions

- [ADR-0001: Agent-Specific Consistency Model](#adr-0001-agent-specific-consistency-model)
```

Create `docs/adrs/ADR-0001-agent-specific-consistency-model.md`:

```markdown
# ADR-0001: Agent-Specific Consistency Model

**Date:** 2026-05-29  
**Status:** Accepted

## Problem

Traditional distributed systems consistency models (eventual, causal, strong) were designed for stateless or deterministically-updated state. Agent systems introduce non-determinism: the same input + instruction produce different outputs depending on model temperature, seed, and context.

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
```

- [ ] **Step 7: Commit initial structure**

```bash
git add docs/ examples/ reference-implementations/ .gitignore README.md CONTRIBUTING.md
git commit -m "docs: initialize documentation structure and pattern templates

- Add README with quick navigation
- Create docs/index.md table of contents
- Initialize all pattern directories and placeholder files
- Add CONTRIBUTING.md guide
- Add ADR template and ADR-0001 on consistency model
- Create examples/ and reference-implementations/ directories

This sets up the skeleton for Phases 1-5 work."
```

---

### Task 2: Write Foundations — Causality & Ordering

**Files:**
- Modify: `docs/foundations/causality-and-ordering.md`
- Create: `examples/observability/causality-example.md`

**Steps:**

- [ ] **Step 1: Write problem statement**

Edit `docs/foundations/causality-and-ordering.md`, replace the Problem Statement section:

```markdown
## Problem Statement

In a distributed agent system, multiple agents may execute concurrently, each making decisions that depend on prior events. When an agent makes a decision at edge, that decision may affect other agents in the cloud. Understanding which decision depends on which prior event — the causal relationship — is critical for debugging, observability, and failure recovery.

Traditional approaches (wall-clock time, request IDs) are insufficient because:
- **Clock skew** — edge devices and cloud clocks may drift; wall-clock time is unreliable
- **Out-of-order delivery** — messages may arrive out of order; wall-clock order doesn't match logical order
- **Concurrency** — multiple agents may execute simultaneously; we need to distinguish causally related events from concurrent ones

How do we track causal dependencies in a distributed agent system?
```

- [ ] **Step 2: Write solution approach**

Replace Solution Approach section:

```markdown
## Solution Approach

**Happens-Before Relation:** An event A "happens-before" event B if A's result was visible to the agent that executed B. Happens-before defines a partial order over events (some events are ordered, others are concurrent).

**Vector Clocks:** Each agent maintains a vector clock — a map of `{agent_id → logical_timestamp}`. When an agent executes, it increments its own clock. When it sends a message, it includes the vector clock. Recipients merge the received clock with their own, taking the max for each agent.

Example:
```
Agent A at time [A:1, B:0, C:0] sends message to Agent B
Agent B receives message, updates its clock to [A:1, B:1, C:0] (max of received and local)
Agent B's subsequent events are [A:1, B:2, C:0], [A:1, B:3, C:0], etc.

Later, Agent C receives a message from B at [A:1, B:3, C:0]
C's clock becomes [A:1, B:3, C:1]
C now knows: this message is causally dependent on events up to B:3 in Agent B, which includes B's receipt of A's message at A:1
```

**Implementing Causality Tracking:**

1. **Trace context propagation** — attach vector clock to every agent invocation (via trace baggage, headers, or parameters)
2. **Log with vector clock** — include vector clock in structured logs: `{"event": "agent_decision", "agent_id": "A", "vector_clock": {"A": 5, "B": 3, "C": 1}}`
3. **Detect causal dependencies in queries** — queries like "what events preceded this agent's decision?" use vector clock comparison
4. **Reconstruct causal history** — from logs, rebuild the DAG of causally-dependent events for debugging

**Limitations:**
- Vector clocks grow with the number of agents (space: O(n) where n = number of agents)
- For swarms of identical agents, use logical timestamps + agent pool identifiers instead
- For very large systems, use hybrid clocks (wall-clock + logical counter) to compress vector clocks
```

- [ ] **Step 3: Write when to use section**

Replace When to Use section:

```markdown
## When to Use

**Use vector clocks when:**
- You have a small number of agents (< 100) whose identities matter
- You need to reconstruct causal history for debugging
- You're building a distributed transaction system (you need to detect conflicts based on causality)

**Use logical timestamps when:**
- You have many identical agents (agent pool) and don't care which specific instance executed
- You care about total order (even if some events are concurrent, you pick an arbitrary order)
- Simplicity is more important than precision

**Use hybrid clocks when:**
- You have moderate agent counts (10-1000) and want to avoid vector clock inflation
- You need both causal ordering AND wall-clock timestamp
```

- [ ] **Step 4: Write trade-offs**

Replace Trade-offs section:

```markdown
## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Vector Clocks** | Precise causality; complete happens-before relation | O(n) space; complex debugging; doesn't directly show wall-clock time |
| **Logical Timestamps** | Simple; works for total ordering | Loses concurrency information; all events appear ordered even if independent |
| **Hybrid Clocks** | Combines causality + wall-clock time; compact | Requires wall-clock synchronization; slightly more complex |
| **Trace IDs + Wall-Clock** | Simple to implement; widely supported | Fails when clocks skew; out-of-order delivery causes confusion |

**Recommendation:** Start with logical timestamps + trace IDs for simplicity. Upgrade to vector clocks if you encounter causality-based bugs (e.g., "why did B make decision X when C hadn't reported the relevant event yet?").
```

- [ ] **Step 5: Write observability hooks**

Replace Observability Hooks section:

```markdown
## Observability Hooks

**Metrics to track:**
- **Vector clock size**: Should grow slowly (linear with agent count). If it grows exponentially, check for clock propagation bugs.
- **Causality resolution success rate**: What % of queries can reconstruct full causal history? (Target: 99%+)

**Logs to examine:**
- When an agent makes a surprising decision, check its input messages' vector clocks
- Look for "clock inversion" — Agent B's clock goes backwards (bad; indicates dropped messages or time travel)

**Queries to support:**
- "Show all events causally before this decision" — use vector clock comparison
- "Show all concurrent events (not in happens-before order)" — agents with non-comparable vector clocks
- "Trace causality from edge agent to cloud decision" — follow vector clock evolution across hops

**Distributed tracing integration:**
- Include vector clock in trace baggage for every span
- Use vector clock to tag spans with causal relationships
```

- [ ] **Step 6: Write example and failure scenarios**

Replace Example and Failure Scenarios sections:

```markdown
## Example: Causality in a Multi-Hop Agent System

**Scenario:** Edge agent A makes a measurement, sends it to cloud agent B for inference, which sends decision to agent C for execution.

```
Time    Agent A                  Agent B                 Agent C
----    -------                  -------                 -------
1       [A:1]                    
        (measure)
        
2                   A->[A:1] 
                     (send to B)
                                  Recv [A:1]
                                  [A:1, B:1]
                                  (receive)
                                  
3                                 [A:1, B:2]
                                  (infer)
                                  
4                   B->[A:1, B:2]
                     (send to C)
                                                        Recv [A:1, B:2]
                                                        [A:1, B:2, C:1]
                                                        (receive)

5                                                       [A:1, B:2, C:2]
                                                        (execute)
```

Vector clocks show:
- Event A:1 happens-before B:1 (A:1 was delivered to B)
- B:1 happens-before B:2 (B's own execution is ordered)
- B:2 happens-before C:1 (B's result was delivered to C)
- A:1 transitively happens-before C:2 (through B)

If C's execution failed, we can trace back: C:2 depends on B:2 depends on B:1 depends on A:1. Check A's measurement, B's inference, etc.

## Failure Scenarios

**Clock inversion:** Agent A increments to [A:5, B:3, C:1], then later executes with [A:3, B:5, C:2]. This indicates:
- Dropped messages (B:3 arrived later than expected)
- Time travel or clock reset on an agent
- **Recovery:** Investigate message delivery; check for network partitions; verify clock sources

**Vector clock explosion:** A system with 10 agents generates vector clocks with 10 entries each. Later, it scales to 100 agents, and vector clocks become huge (100 entries).
- **Recovery:** Use agent pool IDs (group identical agents) or switch to hybrid clocks

**Causality cycles:** A's vector clock shows it depends on B:5, B's shows it depends on A:7. This is impossible (cycles in happens-before).
- **Cause:** Usually dropped messages or clock skew
- **Recovery:** Rebuild vector clocks from logs; detect and discard contradictory events
```

- [ ] **Step 7: Write references**

Replace References section:

```markdown
## References

**Classic Papers:**
- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System" — foundational paper on happened-before
- Mattern, F. (1989). "Virtual Time and Global States of Distributed Systems" — vector clocks

**Related Patterns:**
- [Time, Clocks & Synchronization](time-and-clocks.md) — handling clock skew in practice
- [Distributed Tracing](../patterns/observability/distributed-tracing.md) — implementing causality in tracing systems

**Framework Callouts:**
- **LangGraph:** trace_id is basic; use custom metadata for vector clock propagation
- **Crew:** message passing between agents includes implicit ordering; add vector clocks to decision logs
- **Temporal Workflows:** have native causality tracking via workflow history

**Tools:**
- Jaeger (distributed tracing) — can display causal relationships if instrumented correctly
- ElasticSearch with structured logging — query logs by vector clock for causality analysis
```

- [ ] **Step 8: Create observability example**

Create `examples/observability/causality-example.md`:

```markdown
# Example: Implementing Vector Clock Causality Tracking

## Scenario

Three agents:
- `edge_sensor` (edge) — collects measurements
- `cloud_inference` (cloud) — runs ML inference
- `edge_executor` (edge) — executes decisions

We want to track causality from sensor → inference → executor.

## Code: Vector Clock Wrapper

```python
from typing import Dict
import json

class VectorClock:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.clock: Dict[str, int] = {agent_id: 0}
    
    def increment(self):
        """Increment this agent's logical time"""
        self.clock[self.agent_id] = self.clock.get(self.agent_id, 0) + 1
    
    def merge(self, other_clock: Dict[str, int]):
        """Merge incoming vector clock (from message receipt)"""
        for agent, ts in other_clock.items():
            self.clock[agent] = max(self.clock.get(agent, 0), ts)
        # Then increment own clock
        self.increment()
    
    def to_dict(self) -> Dict[str, int]:
        return dict(self.clock)
    
    def __str__(self) -> str:
        items = [f"{k}:{v}" for k, v in sorted(self.clock.items())]
        return "{" + ", ".join(items) + "}"

# Usage example
def edge_sensor_run():
    vc = VectorClock("edge_sensor")
    vc.increment()
    print(f"[edge_sensor] Starting measurement, clock: {vc}")
    
    measurement = {"value": 42.5}
    
    vc.increment()
    message = {
        "data": measurement,
        "vector_clock": vc.to_dict(),
        "from": "edge_sensor"
    }
    print(f"[edge_sensor] Sending to cloud, clock: {vc}")
    return message

def cloud_inference_run(message):
    vc = VectorClock("cloud_inference")
    
    # Receive message, merge vector clock
    incoming_vc = message["vector_clock"]
    vc.merge(incoming_vc)
    print(f"[cloud_inference] Received message, merged clock: {vc}")
    
    # Run inference
    vc.increment()
    result = {"decision": "execute"}
    
    vc.increment()
    output_message = {
        "data": result,
        "vector_clock": vc.to_dict(),
        "from": "cloud_inference"
    }
    print(f"[cloud_inference] Sending to executor, clock: {vc}")
    return output_message

def edge_executor_run(message):
    vc = VectorClock("edge_executor")
    
    # Receive message, merge vector clock
    incoming_vc = message["vector_clock"]
    vc.merge(incoming_vc)
    print(f"[edge_executor] Received decision, merged clock: {vc}")
    
    # Execute
    vc.increment()
    print(f"[edge_executor] Executing, clock: {vc}")

# Trace execution
m1 = edge_sensor_run()
print()
m2 = cloud_inference_run(m1)
print()
edge_executor_run(m2)
```

**Output:**
```
[edge_sensor] Starting measurement, clock: {edge_sensor:1}
[edge_sensor] Sending to cloud, clock: {edge_sensor:2}

[cloud_inference] Received message, merged clock: {cloud_inference:1, edge_sensor:2}
[cloud_inference] Sending to executor, clock: {cloud_inference:2, edge_sensor:2}

[edge_executor] Received decision, merged clock: {cloud_inference:2, edge_executor:1, edge_sensor:2}
[edge_executor] Executing, clock: {cloud_inference:2, edge_executor:2, edge_sensor:2}
```

## Structured Logging Integration

```python
import json
import logging

logger = logging.getLogger("agent")

class AgentWithVectorClock:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.vc = VectorClock(agent_id)
    
    def log_event(self, event: str, **context):
        """Log event with vector clock"""
        self.vc.increment()
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
            "event": event,
            "vector_clock": self.vc.to_dict(),
            **context
        }
        logger.info(json.dumps(log_entry))
        return self.vc.to_dict()
```

## Querying Causality from Logs

```python
# Reconstruct causal path: which events led to this decision?
def find_causal_ancestors(target_vc, logs):
    """Find all events that causally precede target_vc"""
    ancestors = []
    for log in logs:
        log_vc = log["vector_clock"]
        # Check if log_vc <= target_vc (component-wise)
        if all(log_vc.get(agent, 0) <= target_vc.get(agent, 0) 
               for agent in log_vc.keys()):
            ancestors.append(log)
    return ancestors
```

## Framework Integration Examples

**LangGraph:**
```python
from langgraph.graph import StateGraph

graph = StateGraph(AgentState)

# Add vector clock to state
@graph.node
def edge_sensor(state):
    state.vector_clock.increment()
    state.logs.append({"event": "sensor", "vc": state.vector_clock.to_dict()})
    return state

# Propagate vector clock through graph edges
graph.add_edge("edge_sensor", "cloud_inference", 
               merge_vector_clock=True)
```

**Temporal Workflows:**
Vector clocks are implicit in Temporal's event history; use custom attributes for explicit tracking.
```python
@workflow.run
async def agent_workflow(measurement):
    vc = VectorClock("agent_workflow")
    vc.increment()
    
    # Temporal tracks this in workflow history
    logger.info(f"Vector clock: {vc}")
    
    inference = await activities.run_inference(measurement)
    # Temporal adds happens-before edge automatically
    
    return inference
```
```

- [ ] **Step 9: Commit**

```bash
git add docs/foundations/causality-and-ordering.md examples/observability/causality-example.md
git commit -m "docs: add causality and ordering foundation

- Explain happens-before relation and vector clocks
- Show when to use causality tracking
- Include observability hooks for detecting causality bugs
- Add example: vector clock implementation and structured logging
- Show framework integration (LangGraph, Temporal)
- Document failure scenarios (clock inversion, cycles)"
```

---

### Task 3: Write Foundations — Consistency Models

**Files:**
- Modify: `docs/foundations/consistency-models.md`

**Steps:**

- [ ] **Step 1: Write problem statement**

Edit `docs/foundations/consistency-models.md`, replace all sections:

```markdown
# Consistency Models for Agent State

## Problem Statement

Agent systems maintain shared state: conversation history, tool results, decisions, context. This state is often replicated (edge agents have a copy, cloud agents have a copy) or distributed (one agent holds conversation history, another holds execution state).

Traditional consistency models (eventual, causal, strong) assume deterministic state updates: write X → read X always returns the newly written value. But agents are non-deterministic. The same agent invocation with the same input produces different outputs.

What does "consistency" mean for agent state when the agent's own behavior is probabilistic?

## Solution Approach: Behavioral Consistency

Define consistency in terms of agent **behavior**, not **state identity**:

**Traditional View (Deterministic Systems):**
- Strong consistency: all reads return the most recent write
- Eventual consistency: reads eventually converge to same value

**Agent Systems View (Non-Deterministic):**
- **Behavioral consistency**: agent behavior (latency, token usage, quality) remains predictable even if state replicas diverge
- **State consistency**: conversation history, tool results, execution logs eventually converge across replicas

**Three layers:**

1. **Value Consistency** — agent reads the same conversation history across invocations
2. **Behavioral Consistency** — agent behavior (latency, tokens, quality) meets SLOs even with inconsistent state
3. **Coordination Consistency** — agents coordinating a workflow agree on outcomes (e.g., "payment processed") regardless of state divergence

**For Edge+Cloud Hybrid:**

| Scenario | Strategy |
|----------|----------|
| **Edge agent reading conversation history** | Eventual consistency (local cache + async sync with cloud) |
| **Two edge agents coordinating** | Causal consistency (one sends result, other reads result in happened-before order) |
| **Agent swarm aggregating results** | Quorum consistency (wait for majority of swarm to report before proceeding) |
| **Long-running workflow checkpointing** | Strong consistency at checkpoint boundaries (all agents agree state is saved) |

## When to Use

**Eventual consistency for:**
- Conversation history (delay is acceptable; agent will retrace recent context)
- Observability logs (can be asynchronously synced)
- Metrics (freshness lag is tolerable)

**Causal consistency for:**
- Coordinating results between agents (B's decision depends on A's output)
- Workflow steps (previous step must complete before next)
- Multi-hop messages (order matters)

**Strong consistency for:**
- Financial transactions (debit/credit across agents)
- Critical decisions with human approval
- Checkpoint boundaries (save/restore points)

## Trade-offs

| Consistency Model | Pros | Cons | Edge+Cloud Fit |
|---|---|---|---|
| **Eventual** | Fast (no coordination); high availability under partition | Reads may see stale data; convergence delays | Good (local caching at edge) |
| **Causal** | Respects causality (B sees results of A); intermediate between eventual and strong | Requires tracking dependencies (vector clocks); medium coordination overhead | Good (agent messages have happened-before order) |
| **Strong** | Simplest to reason about (all replicas identical) | Blocks on every write (slow); fails during partition | Poor (can't coordinate across partition) |
| **Quorum** | Balances availability and consistency | Slower than eventual; must configure quorum size | Fair (use quorum within edge tier, eventual edge-to-cloud) |

**Recommendation:** Use eventual consistency as default (fast, available), upgrade to causal consistency when ordering matters, and strong consistency only at critical boundaries (checkpoints, financial operations).

## Observability Hooks

**Metrics to track:**
- **Replication lag**: time between state update on primary and replica (target: < 100ms for edge; < 1s for edge-to-cloud)
- **Consistency violations**: how often do replicas diverge beyond acceptable bound? (target: 0)
- **Causal order violations**: agent B reads state updated by A before B's received A's message? (target: 0)

**Logs to examine:**
- When an agent makes a surprising decision, check if it had stale state
- When a workflow fails, check if agents agreed on prior step's result
- On partition recovery, check state reconciliation time

**Queries to support:**
- "What state did agent X see at time T?" — reconstruct replica state from logs
- "Did agents A and B see consistent data?" — compare state read timestamps and causal order
- "How long to sync state after partition healed?" — measure time from partition detection to state convergence

## Example: Conversation History Consistency

**Scenario:** Multi-turn conversation between user and edge agent. Cloud agent also has access to history (for backup/analytics).

```
Time    Edge Agent                          Cloud Agent
----    ----------                          -----------
1       User: "summarize sales"
        [History: ["summarize..."]]

2       (agent responds)
        [History: ["summarize...", "response"]]

3       (async sync to cloud)
                                            [History: ["summarize..."]]
                                            (lagging by 1 turn)

4       User: "compare to last month"
        [History: ["...", "response", 
                   "compare..."]]

5       (cloud still syncing)                [History: ["summarize...",
                                             "response"]]

6       (edge agent reads from cloud       
        for verification)                   
        
7       (sync completes)
                                            [History: ["...", "response", 
                                             "compare..."]]
```

With eventual consistency, cloud lags behind edge, but that's acceptable because:
- Edge agent (primary) is up-to-date
- Cloud can re-read history from edge if needed
- Async sync eventually brings cloud up to date

If cloud had been asked a question at time 5, it would see old state. Agent might give stale response. That's acceptable because conversation context includes "compare to last month" — cloud can re-request history from edge.

## Failure Scenarios

**State divergence:** Edge agent and cloud agent have different conversation history. Which is correct?
- **Cause:** Network partition, missed sync messages
- **Recovery:** Designate edge as primary (replay history from edge); merge if both have non-overlapping updates
- **Prevention:** Timestamp all updates; prioritize recent updates in merge

**Causal order violation:** Agent B reads state that Agent A hasn't yet sent. B's decision was based on obsolete state.
- **Cause:** Lost message, reordered delivery, clock skew
- **Recovery:** Vector clocks should detect this; reject stale reads
- **Prevention:** Wait for acknowledged delivery before depending on state

**Quorum disagreement:** Agent swarm has 5 agents; 2 report success, 3 report failure. Quorum (3) says failure; 2 out-of-sync agents still think success.
- **Cause:** Slow/unreliable network; agents made decisions before quorum result
- **Recovery:** Force re-sync from authoritative quorum result
- **Prevention:** Don't act on local decision until quorum confirmed

## References

**Related Patterns:**
- [Causality & Ordering](causality-and-ordering.md)
- [Edge State Consistency](../patterns/edge-cloud-deployment/edge-state-consistency.md)
- [Checkpointing Agent State](../patterns/failure-recovery/checkpointing.md)

**Classic Papers:**
- Bailis, P., et al. (2013). "Highly Available Transactions" — consistency models for distributed systems
- Mahajan, P., et al. (2011). "Consistency Analysis in Bloom" — causal consistency

**Framework Callouts:**
- **LangGraph:** conversation history is in memory; add checkpointing for edge-cloud sync
- **Crew:** agent state is per-agent; use message queue for eventual consistency between agents
```

- [ ] **Step 2: Commit**

```bash
git add docs/foundations/consistency-models.md
git commit -m "docs: add consistency models for agent state

- Define behavioral consistency (behavior remains predictable even if state diverges)
- Distinguish state consistency from coordination consistency
- Provide edge+cloud recommendations per scenario
- Include trade-offs: eventual vs causal vs strong vs quorum
- Add observability hooks: replication lag, causal violations
- Example: conversation history consistency across edge+cloud
- Document failure scenarios: divergence, causal violations, quorum disagreement"
```

---

### Task 4: Write Remaining Foundations (Agent Failure Modes, Time/Clocks, Trust)

**Files:**
- Modify: `docs/foundations/agent-failure-modes.md`
- Modify: `docs/foundations/time-and-clocks.md`
- Modify: `docs/foundations/trust-and-byzantine.md`

**Steps (abbreviated — apply same structure as Tasks 2-3):**

For each file:

1. Write **Problem Statement** (250-350 words)
2. Write **Solution Approach** (400-500 words)
3. Write **When to Use** section (150-200 words)
4. Write **Trade-offs** table
5. Write **Observability Hooks** section (200 words)
6. Write **Example** with code or scenario (300-400 words)
7. Write **Failure Scenarios** (250-350 words)
8. Write **References** section

**`docs/foundations/agent-failure-modes.md` — key topics:**
- Non-determinism (same input → different outputs due to temperature, seed)
- Context degradation (behavior changes as context window fills)
- Token depletion (agent fails when token budget exhausted)
- Inference timeout (cloud inference takes too long; edge times out)
- Hallucination under resource pressure
- Context window thrashing (agent cycles through context compaction)

**`docs/foundations/time-and-clocks.md` — key topics:**
- Clock skew (edge device clock drifts from cloud)
- Event-time vs wall-clock (agent timestamps may not reflect real time)
- Timeout detection in slow networks (how long to wait before declaring failure?)
- Leap seconds and NTP synchronization
- Vector clocks as alternative to wall-clock

**`docs/foundations/trust-and-byzantine.md` — key topics:**
- Can agents be trusted to report state accurately?
- Byzantine fault tolerance for agent swarms (detect when agent lies)
- Cryptographic commitment (agent signs decision, can't later claim it was different)
- Voting/consensus among untrusted agents
- Trust boundaries (edge agents at boundary with untrusted external agents)

- [ ] **Step 3: Commit all three files**

```bash
git add docs/foundations/agent-failure-modes.md docs/foundations/time-and-clocks.md docs/foundations/trust-and-byzantine.md
git commit -m "docs: complete foundations layer

- Agent Failure Modes: non-determinism, context degradation, token depletion, timeouts, hallucinations
- Time, Clocks & Synchronization: clock skew, event-time, timeout detection, NTP, vector clocks
- Trust & Byzantine Agents: agent truthfulness, BFT for swarms, cryptographic commitment, consensus

Foundations layer complete. Ready for Core Patterns in Phase 2."
```

---

### Task 5: Write Observability Patterns (4 patterns)

**Files:**
- Modify: `docs/patterns/observability/distributed-tracing.md`
- Modify: `docs/patterns/observability/understanding-decisions.md`
- Modify: `docs/patterns/observability/logging-strategies.md`
- Modify: `docs/patterns/observability/agent-health-metrics.md`
- Create: `examples/observability/tracing-setup.py`
- Create: `examples/observability/metrics-example.py`

**Steps:**

For each observability pattern, follow the structure:

1. **Problem Statement** (what observability challenge?)
2. **Solution Approach** (how do we make agents observable?)
3. **When to Use**
4. **Trade-offs**
5. **Observability Hooks** (meta: how do we verify observability is working?)
6. **Example** (code or configuration)
7. **Failure Scenarios**
8. **References**

**`distributed-tracing.md` — key topics:**
- Trace context propagation (OpenTelemetry, trace ID, span ID, baggage)
- Instrument each agent call as a span (input, output, vector clock)
- Baggage: carry metadata (agent pool, edge region, priority) across span boundaries
- Sampling strategies (trace every call? sample 1%? adaptive sampling based on error rate?)
- Cross-partition tracing (tracing from edge agent through cloud agent to executor)
- Framework integration (LangGraph, Crew, AutoGen instrumentation)

**`understanding-decisions.md` — key topics:**
- Token attribution: which input tokens influenced which output tokens?
- Attention visualization (if available from model)
- Decision tree reconstruction (agent made choice A because condition X was true)
- Embedding inspection (why did agent cluster this with that?)
- Prompt analysis (what system prompt influenced this decision?)
- Model confidence/uncertainty signals

**`logging-strategies.md` — key topics:**
- Structured logging (JSON, not free-form text)
- Log levels for agents (DEBUG: each token; INFO: decision checkpoints; ERROR: failures)
- Idempotency keys in logs (detect retries, replays)
- Capturing non-determinism sources (seed, temperature, model version)
- Log sampling (can't log every token, sample intelligently)
- Correlated logs (link logs from different agents in same workflow)

**`agent-health-metrics.md` — key topics:**
- Latency metrics (p50, p99, max per agent or per agent pool)
- Token consumption (actual vs budgeted, per turn, per conversation)
- Quality metrics (does agent output match expected type? pass validation?)
- Error rates (timeouts, token depletion, inference failures)
- SLA compliance (% of calls met SLO, % of conversations met end-to-end SLO)
- Per-edge-region metrics (latency differs across regions)

- [ ] **Step 1: Write distributed-tracing.md**

(Follow pattern from Task 2 — problem, solution, trade-offs, hooks, example, failures, refs)

Include example:

```python
# Example: Distributed tracing for agent call
from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup Jaeger exporter
jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(...)

tracer = trace.get_tracer(__name__)

def run_agent_with_tracing(agent_id: str, input_data: dict) -> dict:
    # Start trace span
    with tracer.start_as_current_span(f"agent.{agent_id}") as span:
        # Attach context as baggage
        baggage.set_baggage("agent_id", agent_id)
        baggage.set_baggage("vector_clock", str(vector_clock))
        
        span.set_attribute("agent.id", agent_id)
        span.set_attribute("agent.input_tokens", len(input_data["text"]))
        
        # Run agent
        result = agent.run(input_data)
        
        # Log output
        span.set_attribute("agent.output_tokens", len(result["text"]))
        span.add_event("agent_decision", 
                       attributes={"decision": result["action"]})
        
        return result
```

- [ ] **Step 2-5: Write remaining three observability patterns**

(Apply same structure; include code examples)

- [ ] **Step 6: Create example files**

Create `examples/observability/tracing-setup.py` with complete working tracing setup.
Create `examples/observability/metrics-example.py` with Prometheus metrics examples.

- [ ] **Step 7: Commit**

```bash
git add docs/patterns/observability/ examples/observability/
git commit -m "docs: add observability patterns

- Distributed Tracing: context propagation, trace baggage, cross-partition tracing
- Understanding Model Decisions: token attribution, confidence signals
- Logging Strategies: structured logging, idempotency keys, non-determinism capture
- Agent Health Metrics: latency, tokens, quality, SLA compliance

Includes OpenTelemetry examples and Prometheus metrics integration.
Observability patterns complete."
```

---

## Phase 2: Predictability, Resource Allocation (Layers 2.2 - 2.3)

**Deliverable:** Readers can forecast agent behavior and allocate resources fairly.

**Estimated effort:** 2-3 weeks (7-9 tasks)

### Task 6-14: Write Core Patterns (Predictability, Resource Allocation)

(Each follows the pattern structure: problem, solution, trade-offs, hooks, example, failures, refs)

**Predictability patterns (5 tasks):**
- Context Window Management
- Behavior Degradation
- Token Budgeting
- Testing & Validation
- SLOs for Agentic Workloads

**Resource Allocation patterns (4 tasks):**
- Fair Queuing & Scheduling
- Reservation vs. Burst
- Context Window Allocation
- Priority Queues & Preemption

Each task:
1. Write pattern document (follow Task 2 structure)
2. Create example code or configuration
3. Commit

*Abbreviated here for space; each task is 60-90 minutes.*

---

## Phase 3: Failure Recovery, Edge+Cloud Deployment (Layers 2.4 - 3)

**Deliverable:** Readers can build reliable agentic workflows and deploy agents across edge+cloud.

**Estimated effort:** 3-4 weeks (9-12 tasks)

### Task 15-26: Write Failure Recovery & Deployment Patterns

**Failure Recovery patterns (4 tasks):**
- Idempotency & Replay
- Checkpointing Agent State
- Recovery Strategies
- ACID-like Guarantees

**Edge+Cloud Deployment patterns (5 tasks):**
- Agent Placement
- Network Partition Handling
- Asynchronous Coordination
- Local vs. Remote Inference
- Edge State Consistency

Each task: 60-90 minutes (same structure as Phase 2).

---

## Phase 4: Integration Patterns, Case Study (Layers 4-5)

**Deliverable:** Readers see all patterns working together; understand how to apply to their systems.

**Estimated effort:** 2-3 weeks (5-7 tasks)

### Task 27-31: Write Integration Patterns (4 tasks)

- Single-Agent at Scale
- Multi-Agent Coordination
- Agent Swarms
- Hierarchical Agent Networks

### Task 32-35: Write Case Study (3-4 tasks)

**Case Study: Large-Scale AI Analytics Engine**

- **Task 32:** Scenario Overview — system architecture, agents, deployment
- **Task 33:** Detailed Architecture — topology, data flow, state management
- **Task 34:** Pattern Application — walkthrough showing which patterns apply where
- **Task 35:** Failure Scenarios & Recovery — demonstrate observability + recovery

---

## Phase 5: Polish, ADRs, Final Navigation (maintenance)

**Deliverable:** Project is complete, well-organized, ready for readers.

**Estimated effort:** 1-2 weeks (4-5 tasks)

### Task 36: Write Remaining ADRs

- ADR-0002: Vector Clock vs. Logical Timestamp Trade-off
- ADR-0003: Token Budgeting Strategy (reserved vs. burn)
- ADR-0004: Edge+Cloud Consistency Model Selection

### Task 37: Build Interactive Navigation

- Update `docs/index.md` with cross-references
- Add "Next reading" suggestions at end of each pattern
- Create decision tree: "I want to [observe|predict|allocate|recover]. Which pattern?"

### Task 38: Create Examples Gallery

- Index all code examples by pattern
- Add "run this example" quick-start for each

### Task 39: Final Review & Polish

- Check all links
- Consistent terminology across docs
- Proof-read

### Task 40: Commit & Deploy

- Final commit
- Push to GitHub
- Update portfolio site navigation

---

## Success Criteria Checklist

- [ ] All 5 foundations written and committed
- [ ] All 20 core patterns written (observability, predictability, resource allocation, failure recovery)
- [ ] All 5 edge+cloud deployment patterns written
- [ ] All 4 integration patterns written
- [ ] Case study complete (scenario, architecture, pattern application, failures)
- [ ] All code examples runnable or reproducible
- [ ] ADRs documenting key decisions
- [ ] Navigation/index complete and linked
- [ ] Readers can find answers to: "How do I observe agents?", "How do I predict behavior?", "How do I allocate resources?", "How do I recover from failures?", "How do I deploy edge+cloud?"
- [ ] Project is in `chakraview-distributed-systems-patterns` on GitHub Pages

---

## Branching Strategy

Main phase branches:
- `main` — always clean, merged PRs only
- Feature branches per pattern: `docs/observability/distributed-tracing`, `docs/case-study/scenario`, etc.

Commit often (after each task).

---

## Estimated Timeline

| Phase | Tasks | Duration | Status |
|-------|-------|----------|--------|
| 1: Foundations + Observability | 1-5 | 2-3 weeks | — |
| 2: Predictability + Resource Allocation | 6-14 | 2-3 weeks | — |
| 3: Failure Recovery + Deployment | 15-26 | 3-4 weeks | — |
| 4: Integration + Case Study | 27-35 | 2-3 weeks | — |
| 5: Polish & Deployment | 36-40 | 1-2 weeks | — |
| **Total** | **40 tasks** | **10-15 weeks** | — |

Phases can overlap (start Phase 2 while Phase 1 is in progress) to reduce total time.

