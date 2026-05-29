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
