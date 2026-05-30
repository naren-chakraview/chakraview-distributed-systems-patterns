# Pattern Cross-References

This file maintains links from pattern documentation to reference implementation code.

## Zero Trust for Agents

**Documentation:** `docs/foundations/zero-trust-for-agents.md`

**Code Examples:**
- Agent identity types: `trust/agent_identity.py:1-60`
- Delegation token with OBO: `trust/delegation_token.py:1-150`
- Policy enforcer: `trust/policy_enforcer.py:1-100`
- Identity registry: `trust/identity_registry.py:1-80`
- Unit tests: `trust/tests/test_policy_enforcer.py`
- Policy definitions: `trust/policies.yaml`
- Proto definition: `shared/proto/messages.proto:AgentIdentity message`

**Related Patterns:**
- Trust & Byzantine Agents: covers agent OUTPUT verification; this covers agent IDENTITY
- Hierarchical Agent Networks: deployment topology this pattern secures
# Pattern to Code References

Complete index mapping distributed systems patterns to their implementation examples and code locations.

## Patterns Index

### Predictability Patterns

#### Token Budgeting
- **Documentation**: `docs/patterns/predictability/token-budgeting.md`
- **Key Files**:
  - Reference Implementation: `reference-implementations/agents/` (intent_agent.py, fraud_agent.py)
  - Fixtures: `tests/conftest.py` → `MockIntentAgent.execute()` (lines ~75-95)
  - Integration Tests: `tests/integration/test_full_pipeline.py` → `test_token_budgeting_across_agents()` (lines ~150-180)
- **Concepts**:
  - Budget tracking per agent execution
  - Token consumption estimation
  - Budget enforcement across distributed agents
- **Related Tests**:
  - `test_token_budgeting_across_agents`: Verifies token consumption stays within budget
  - `test_degradation_mode_behavior`: Tests graceful degradation when budget is exhausted

#### Behavior Degradation
- **Documentation**: `docs/patterns/predictability/behavior-degradation.md`
- **Key Files**:
  - Agent Implementation: Intent agent `_degrade_to_keyword_matching()` method
  - Test Coverage: `tests/integration/test_full_pipeline.py` → `test_degradation_mode_behavior()` (lines ~250-275)
- **Concepts**:
  - Graceful degradation to fallback implementations
  - Reduced confidence scores in degraded mode
  - Minimal token consumption for fallbacks
- **Pattern Demonstration**:
  - When token budget exhausted, switch from full LLM inference to keyword matching

#### Context Window Management
- **Documentation**: `docs/patterns/predictability/context-window-management.md`
- **Key Files**:
  - Agent Fixtures: `tests/conftest.py` → `AgentConfig` class (lines ~30-40)
  - Pipeline Tests: `tests/integration/test_full_pipeline.py` → Full pipeline flow
- **Concepts**:
  - max_context_tokens configuration
  - Context pruning strategies
  - Sliding window management

#### Testing and Validation
- **Documentation**: `docs/patterns/predictability/testing-and-validation.md`
- **Key Files**:
  - Test Suite: `tests/integration/test_full_pipeline.py` (entire file)
  - Fixtures: `tests/conftest.py` (mock agents and configurations)
- **Integration Tests Included**:
  - `test_user_to_segment_flow`: Multi-stage pipeline validation
  - `test_vector_clock_propagation`: Causality tracking
  - `test_parallel_agent_execution`: Concurrent execution safety
  - `test_consistency_across_pipeline_runs`: Determinism validation

#### Agentic SLOs
- **Documentation**: `docs/patterns/predictability/agentic-slos.md`
- **Key Files**:
  - Config: `tests/conftest.py` → `AgentConfig.latency_budget_ms` (line 35)
  - Tracking: Integration tests measure execution time and token usage
- **SLO Types**:
  - Latency (latency_budget_ms)
  - Token consumption (token_budget)

### Failure Recovery Patterns

#### Idempotency and Replay
- **Documentation**: `docs/patterns/failure-recovery/idempotency-and-replay.md`
- **Key Files**:
  - Test: `tests/integration/test_full_pipeline.py` → `test_consistency_across_pipeline_runs()` (lines ~210-225)
- **Concepts**:
  - Same input produces same output
  - Safe to retry operations
  - Transaction ID tracking

#### Recovery Strategies
- **Documentation**: `docs/patterns/failure-recovery/recovery-strategies.md`
- **Key Files**:
  - Test: `tests/integration/test_full_pipeline.py` → `test_error_handling_in_pipeline()` (lines ~230-245)
- **Patterns**:
  - Graceful degradation on error
  - Agent restart capability
  - Fallback mechanisms

#### Checkpointing
- **Documentation**: `docs/patterns/failure-recovery/checkpointing.md`
- **Key Files**:
  - Vector Clock State: `shared/python/vector_clock.py`
  - Result Objects: `tests/conftest.py` → All result dataclasses (lines ~50-110)

#### ACID Guarantees
- **Documentation**: `docs/patterns/failure-recovery/acid-guarantees.md`
- **Key Files**:
  - State Management: `tests/conftest.py` → Agent state tracking
  - Verification: Integration tests verify state consistency

### Observability Patterns

#### Distributed Tracing
- **Documentation**: `docs/patterns/observability/distributed-tracing.md`
- **Key Files**:
  - Infrastructure: `examples/local-dev/docker-compose.yml` → Jaeger service
  - Test: `tests/integration/test_full_pipeline.py` → `test_trace_id_correlation()` (lines ~240-255)
  - Foundation: `shared/python/vector_clock.py`
- **Tracing Elements**:
  - Trace IDs for request correlation
  - Vector clocks for causal relationships
  - Structured logging integration

#### Logging Strategies
- **Documentation**: `docs/patterns/observability/logging-strategies.md`
- **Key Files**:
  - Logger Implementation: `shared/python/logging.py`
  - Usage: All agent classes use StructuredLogger
- **Log Types**:
  - Token consumption
  - Decision reasoning
  - Vector clock state
  - Error tracking

#### Understanding Decisions
- **Documentation**: `docs/patterns/observability/understanding-decisions.md`
- **Key Files**:
  - Pattern in Code: Intent agent `_build_reasoning()` method
  - Test Coverage: `tests/integration/test_full_pipeline.py` validates reasoning fields
- **Transparency**:
  - Confidence scores in results
  - Reasoning explanations
  - Alternative options tracking

#### Agent Health Metrics
- **Documentation**: `docs/patterns/observability/agent-health-metrics.md`
- **Key Files**:
  - Fixtures: `tests/conftest.py` → Mock agents track call_count and token_usage
  - Test: Integration tests verify health metrics
- **Metrics Tracked**:
  - Call count per agent
  - Token consumption summary
  - Vector clock state
  - Result timestamps

### Edge-Cloud Deployment Patterns

#### Agent Placement
- **Documentation**: `docs/patterns/edge-cloud-deployment/agent-placement.md`
- **Key Files**:
  - Fixture Separation: `tests/conftest.py`
    - Edge agents: intent_agent, fraud_agent (budgets: 5000)
    - Cloud agents: trends_agent, segmentation_agent (budgets: 10000)
- **Placement Strategy**:
  - Lighter agents with lower budgets at edge
  - Heavier analysis at cloud

#### Async Coordination
- **Documentation**: `docs/patterns/edge-cloud-deployment/async-coordination.md`
- **Key Files**:
  - Test: `tests/integration/test_full_pipeline.py` → `test_parallel_agent_execution()` (lines ~190-210)
  - Implementation: All fixtures use `async def execute()`
- **Patterns**:
  - Non-blocking message passing
  - asyncio.gather() for parallel execution

#### Edge State Consistency
- **Documentation**: `docs/patterns/edge-cloud-deployment/edge-state-consistency.md`
- **Key Files**:
  - Vector Clocks: `tests/conftest.py` → VectorClock class (lines ~35-52)
  - Test: `test_vector_clock_propagation()` validates consistency
- **Consistency Mechanism**:
  - Vector clocks track causality
  - Merge operations maintain consistency

#### Partition Handling
- **Documentation**: `docs/patterns/edge-cloud-deployment/partition-handling.md`
- **Key Files**:
  - Error Handling: `tests/integration/test_full_pipeline.py` → `test_error_handling_in_pipeline()`
- **Strategies**:
  - Graceful degradation
  - Local fallbacks
  - Retry mechanisms

#### Inference Strategies
- **Documentation**: `docs/patterns/edge-cloud-deployment/inference-strategies.md`
- **Key Files**:
  - Edge Inference: Intent and Fraud agents (edge-optimized)
  - Cloud Inference: Trends and Segmentation agents (compute-intensive)
  - Demo: `examples/pattern-demos/` demonstrates inference options

### Resource Allocation Patterns

#### Context Allocation
- **Documentation**: `docs/patterns/resource-allocation/context-allocation.md`
- **Key Files**:
  - Config: `tests/conftest.py` → AgentConfig (line 32: max_context_tokens)
- **Allocation Strategy**:
  - Per-agent context budgets
  - Pruning for maintenance

#### Token Budgeting (cross-ref)
- **See**: Predictability section above

#### Fair Queuing
- **Documentation**: `docs/patterns/resource-allocation/fair-queuing.md`
- **Key Files**:
  - Queue Service: `examples/local-dev/docker-compose.yml` → queue service
  - Infrastructure: See Docker Compose section

#### Priority Queues
- **Documentation**: `docs/patterns/resource-allocation/priority-queues.md`
- **Key Files**:
  - Infrastructure: Queue service implementation
  - Demo: `examples/pattern-demos/` includes priority queue demonstration

#### Reservation vs. Burst
- **Documentation**: `docs/patterns/resource-allocation/reservation-vs-burst.md`
- **Key Files**:
  - Token Budget Config: Fixed allocations model reservation

### Integration Patterns

#### Single-Agent Scale
- **Documentation**: `docs/patterns/integration/single-agent-scale.md`
- **Key Files**:
  - Test: `tests/integration/test_full_pipeline.py` → Multiple calls to single agent

#### Hierarchical Networks
- **Documentation**: `docs/patterns/integration/hierarchical-networks.md`
- **Key Files**:
  - Pipeline Example: `test_user_to_segment_flow()` shows 3-stage hierarchy

#### Multi-Agent Coordination
- **Documentation**: `docs/patterns/integration/multi-agent-coordination.md`
- **Key Files**:
  - Test: `tests/integration/test_full_pipeline.py` → `test_user_to_segment_flow()` (lines ~25-65)
  - Vector Clock Merging: `test_vector_clock_propagation()` (lines ~80-110)

#### Agent Swarms
- **Documentation**: `docs/patterns/integration/agent-swarms.md`
- **Key Files**:
  - Test: `tests/integration/test_full_pipeline.py` → `test_parallel_agent_execution()` (lines ~190-210)
  - Implementation: Parallel asyncio.gather() execution

## Foundation Concepts

Each pattern is grounded in foundational concepts:

### Time and Clocks
- **Documentation**: `docs/foundations/time-and-clocks.md`
- **Code**: `shared/python/vector_clock.py`
- **Tests**: `test_vector_clock_propagation()`

### Causality and Ordering
- **Documentation**: `docs/foundations/causality-and-ordering.md`
- **Code**: Vector clock merge operations
- **Tests**: `test_consistency_across_pipeline_runs()`

### Consistency Models
- **Documentation**: `docs/foundations/consistency-models.md`
- **Tests**: `test_consistency_across_pipeline_runs()`

### Agent Failure Modes
- **Documentation**: `docs/foundations/agent-failure-modes.md`
- **Tests**: `test_error_handling_in_pipeline()`

### Trust and Byzantine
- **Documentation**: `docs/foundations/trust-and-byzantine.md`
- **Related**: Error handling and verification

## Demo Scripts

Runnable demonstrations of key patterns:

- `examples/pattern-demos/demo_token_budgeting.py` - Token budget exhaustion and degradation
- `examples/pattern-demos/demo_causality.py` - Vector clock and causal ordering
- `examples/pattern-demos/demo_tracing.py` - Distributed tracing setup (in Jaeger)

## Infrastructure and Deployment

### Docker Compose Services
- **File**: `examples/local-dev/docker-compose.yml`
- **Services**:
  - postgres: State persistence
  - redis: Caching and session management
  - jaeger: Distributed tracing backend
  - queue: Message queuing for async coordination

### Local Development
- **File**: `examples/local-dev/README.md`
- **Quick Start**: How to run services locally

## Quick Navigation

**Finding implementation for a pattern:**

1. Look up pattern in this file → Get documentation path
2. Read docs/*.md for concepts
3. Check "Key Files" section → Implementation locations
4. Review test files → Integration test examples
5. Run demo script → See it in action

**Adding a new pattern:**

1. Write pattern documentation in `docs/patterns/*/`
2. Add "Code References" section with file paths and line numbers
3. Create or update integration test in `tests/integration/`
4. Update this file with new pattern entry
5. Create demo script in `examples/pattern-demos/` if appropriate
