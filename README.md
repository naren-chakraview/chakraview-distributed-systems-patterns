# AI Analytics Engine — Reference Implementation

Reference implementation of distributed systems patterns and practices for LLM-backed agent systems deployed in edge+cloud hybrid environments.

This project documents and demonstrates patterns for **observability**, **predictability**, **resource allocation**, and **failure recovery** in agentic systems — challenges that emerge when agents are distributed across networks.

## Key Features

- **Complete Pattern Library** — 30+ documented patterns covering all major challenges in distributed agent systems
- **Working Reference Implementation** — Edge and cloud agents demonstrating real patterns in Python
- **Integration Tests** — Full-pipeline tests validating pattern interactions
- **Local Development Environment** — Docker Compose setup with PostgreSQL, Redis, Jaeger, RabbitMQ, Prometheus, and Grafana
- **Runnable Demos** — Executable demonstrations of token budgeting, causality tracking, and distributed tracing
- **Architecture Decision Records** — Rationales behind key design choices

## Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Git

### 1. Start Infrastructure

```bash
cd examples/local-dev
docker-compose up -d
```

Wait for all services to be healthy:
```bash
docker-compose ps
```

### 2. Run Integration Tests

```bash
cd ../..
pip install pytest pytest-asyncio
pytest tests/integration/test_full_pipeline.py -v
```

### 3. Run Pattern Demos

```bash
# Token budgeting and behavior degradation
python examples/pattern-demos/demo_token_budgeting.py

# Vector clocks and causality
python examples/pattern-demos/demo_causality.py
```

### 4. View Observability

- **Jaeger Distributed Tracing**: http://localhost:16686
- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3000 (admin/agents_password)
- **RabbitMQ Queue UI**: http://localhost:15672 (agents_user/agents_password)
- **PostgreSQL**: localhost:5432 (agents_user/agents_password)

## Architecture Overview

### System Design

```
User Request
    ↓
┌───────────────────────────────────────┐
│   Edge Tier (Low-latency, Constrained)│
├───────────────────────────────────────┤
│ ├─ Intent Detection Agent              │
│ │  └─ Token Budget: 5000               │
│ │  └─ Behavior Degradation: Keyword    │
│ │                                      │
│ └─ Fraud Detection Agent               │
│    └─ Token Budget: 5000               │
│    └─ Risk Assessment                  │
└───────────────────────────────────────┘
    ↓ (async message via queue)
┌───────────────────────────────────────┐
│   Cloud Tier (High-compute)           │
├───────────────────────────────────────┤
│ ├─ Trends Analysis Agent               │
│ │  └─ Token Budget: 10000              │
│ │  └─ Full LLM Inference               │
│ │                                      │
│ └─ Segmentation Agent                  │
│    └─ Token Budget: 10000              │
│    └─ Customer Profiling               │
└───────────────────────────────────────┘
    ↓
 Database (PostgreSQL)
 Cache (Redis)
 Tracing (Jaeger)
```

### Pattern Categories

#### Predictability (4 patterns)
How do we ensure agents behave predictably despite resource constraints?

- **[Token Budgeting](docs/patterns/predictability/token-budgeting.md)** — Allocate and enforce LLM token budgets per agent
- **[Behavior Degradation](docs/patterns/predictability/behavior-degradation.md)** — Graceful fallbacks when resources exhausted
- **[Context Window Management](docs/patterns/predictability/context-window-management.md)** — Manage attention window as it fills
- **[Agentic SLOs](docs/patterns/predictability/agentic-slos.md)** — Define and monitor service levels for agents

#### Observability (4 patterns)
How do we understand what agents are doing and why?

- **[Distributed Tracing](docs/patterns/observability/distributed-tracing.md)** — End-to-end request tracing with causality
- **[Logging Strategies](docs/patterns/observability/logging-strategies.md)** — Structured logging for distributed debugging
- **[Understanding Model Decisions](docs/patterns/observability/understanding-decisions.md)** — Transparency into agent reasoning
- **[Agent Health Metrics](docs/patterns/observability/agent-health-metrics.md)** — Key metrics and SLI definitions

#### Resource Allocation (4 patterns)
How do we allocate scarce resources fairly?

- **[Token Budgeting](docs/patterns/resource-allocation/context-allocation.md)** — Allocate context windows
- **[Fair Queuing](docs/patterns/resource-allocation/fair-queuing.md)** — Serve all agents equitably
- **[Priority Queues](docs/patterns/resource-allocation/priority-queues.md)** — Handle urgent vs. batch workloads
- **[Reservation vs. Burst](docs/patterns/resource-allocation/reservation-vs-burst.md)** — Balance predictability and efficiency

#### Failure Recovery (4 patterns)
How do we recover from failures?

- **[Idempotency and Replay](docs/patterns/failure-recovery/idempotency-and-replay.md)** — Safe retries
- **[Recovery Strategies](docs/patterns/failure-recovery/recovery-strategies.md)** — Multiple recovery paths
- **[Checkpointing](docs/patterns/failure-recovery/checkpointing.md)** — Save and restore state
- **[ACID Guarantees](docs/patterns/failure-recovery/acid-guarantees.md)** — Transaction semantics

#### Edge-Cloud Deployment (5 patterns)
How do we coordinate agents across edge and cloud?

- **[Agent Placement](docs/patterns/edge-cloud-deployment/agent-placement.md)** — Where to run each agent
- **[Edge State Consistency](docs/patterns/edge-cloud-deployment/edge-state-consistency.md)** — Keeping edge and cloud in sync
- **[Async Coordination](docs/patterns/edge-cloud-deployment/async-coordination.md)** — Non-blocking message passing
- **[Partition Handling](docs/patterns/edge-cloud-deployment/partition-handling.md)** — Surviving network failures
- **[Inference Strategies](docs/patterns/edge-cloud-deployment/inference-strategies.md)** — When to use edge vs. cloud

#### Integration (4 patterns)
How do we coordinate multiple agents?

- **[Single-Agent Scale](docs/patterns/integration/single-agent-scale.md)** — Scaling one agent vertically
- **[Multi-Agent Coordination](docs/patterns/integration/multi-agent-coordination.md)** — Sequential pipelines
- **[Hierarchical Networks](docs/patterns/integration/hierarchical-networks.md)** — Supervisor + worker architecture
- **[Agent Swarms](docs/patterns/integration/agent-swarms.md)** — Parallel, independent agents

#### Foundation Concepts (5 concepts)
- **[Causality and Ordering](docs/foundations/causality-and-ordering.md)** — Happened-before relationships via vector clocks
- **[Time and Clocks](docs/foundations/time-and-clocks.md)** — Logical vs. wall-clock time
- **[Consistency Models](docs/foundations/consistency-models.md)** — What guarantees do agents provide?
- **[Agent Failure Modes](docs/foundations/agent-failure-modes.md)** — How agents can fail
- **[Trust and Byzantine](docs/foundations/trust-and-byzantine.md)** — Handling untrustworthy agents

## Code Structure

```
reference-implementations/
├── shared/
│   ├── python/
│   │   ├── agent_base.py       # Base class with token budgeting & vector clocks
│   │   ├── vector_clock.py     # Causality tracking
│   │   └── logging.py          # Structured logging
│   └── proto/
│       └── messages.proto      # Message definitions
├── edge_agents/
│   ├── intent_agent.py         # Detect user intent; degrade on budget exhaustion
│   ├── fraud_agent.py          # Assess transaction fraud risk
│   └── tests/
│       └── test_*.py           # Unit tests
└── cloud_agents/
    ├── trends_agent.py         # Analyze temporal trends
    ├── segmentation_agent.py   # Customer segmentation
    └── tests/
        └── test_*.py           # Unit tests

tests/
├── conftest.py                 # Pytest fixtures for all agents
├── integration/
│   └── test_full_pipeline.py   # End-to-end pipeline tests
│       ├── test_user_to_segment_flow()
│       ├── test_vector_clock_propagation()
│       ├── test_token_budgeting_across_agents()
│       ├── test_parallel_agent_execution()
│       └── ... (8 total tests)

examples/
├── local-dev/
│   ├── docker-compose.yml      # Full infrastructure stack
│   ├── prometheus.yml          # Metrics scraping config
│   └── README.md               # Setup and usage guide
└── pattern-demos/
    ├── demo_token_budgeting.py # Run and watch budget exhaustion
    ├── demo_causality.py       # Vector clock mechanics
    └── demo_tracing.py         # Jaeger integration (coming soon)

docs/
├── foundations/                # Core concepts
├── patterns/                   # 30+ pattern documents
├── adrs/                       # Architecture decisions
├── case-study/                 # Full example: fraud detection analytics
└── superpowers/                # Design specs and implementation plans

PATTERN_LINKS.md                # Complete pattern-to-code cross-reference
```

## Pattern Demonstrations

### Running Demos

Each demo is self-contained and runnable without infrastructure:

```bash
# Watch token budgeting in action (budget exhaustion → degradation)
python examples/pattern-demos/demo_token_budgeting.py

# Understand vector clocks and causality
python examples/pattern-demos/demo_causality.py
```

### Integration Tests

Full-pipeline tests demonstrating pattern interactions:

```bash
# Run all integration tests
pytest tests/integration/test_full_pipeline.py -v

# Run specific test
pytest tests/integration/test_full_pipeline.py::test_user_to_segment_flow -v

# 8 tests covering:
# - User intent → fraud detection → segmentation pipeline
# - Vector clock propagation and causality
# - Token consumption across agents
# - Parallel agent execution
# - Agent isolation and state consistency
# - Error handling and recovery
# - Distributed tracing setup
# - Degradation mode behavior
```

## Learning Path

### For Architects
1. Start with [Foundations](docs/foundations/) — understand causality, consistency, failure modes
2. Read [ADRs](docs/adrs/) — see design rationales
3. Review [Edge-Cloud Deployment](docs/patterns/edge-cloud-deployment/) — how to distribute agents
4. Study [Case Study](docs/case-study/) — patterns in context

### For Implementers
1. Explore [Reference Implementation](reference-implementations/) — see patterns in code
2. Run [Integration Tests](tests/integration/) — verify patterns work together
3. Try [Pattern Demos](examples/pattern-demos/) — hands-on understanding
4. Use [Local Environment](examples/local-dev/) — develop with full infrastructure

### For Operators
1. Study [Observability Patterns](docs/patterns/observability/) — monitoring and debugging
2. Review [Failure Recovery](docs/patterns/failure-recovery/) — resilience strategies
3. Check [Agentic SLOs](docs/patterns/predictability/agentic-slos.md) — what to measure
4. Set up [Local Environment](examples/local-dev/) — run monitoring stack

## Navigation

- **Find a pattern by name**: See [PATTERN_LINKS.md](PATTERN_LINKS.md)
- **Find code for a pattern**: Each pattern doc has "Code References" section
- **Find tests for a pattern**: See `tests/integration/test_full_pipeline.py`
- **Learn by example**: Run `examples/pattern-demos/demo_*.py`
- **Understand the system**: Read `docs/case-study/architecture.md`

## Key Metrics and SLIs

### Agent Health
- Token consumption vs. budget
- Latency vs. SLO deadline
- Success rate (non-degraded execution)
- Decision quality (confidence scores)

### System Health
- Request latency (p50, p99)
- Error rate
- Queue depth
- Cache hit rate

### Infrastructure
- Database query latency
- Redis cache performance
- Message queue throughput
- Trace completion rate

See [Agent Health Metrics](docs/patterns/observability/agent-health-metrics.md) for complete SLI definitions.

## Development

### Running Tests

```bash
# Install dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=reference_implementations --cov-report=html

# Run specific pattern tests
pytest tests/integration/test_full_pipeline.py -k token_budgeting
```

### Adding a New Pattern

1. **Document it**: Create `docs/patterns/<category>/<pattern-name>.md`
2. **Add code references**: Include file paths and line numbers
3. **Create tests**: Add integration test to `tests/integration/test_full_pipeline.py`
4. **Demo it**: Create runnable example in `examples/pattern-demos/`
5. **Update index**: Add entry to [PATTERN_LINKS.md](PATTERN_LINKS.md)

## Deployment Options

### Option 1: Local Development
- Use `examples/local-dev/docker-compose.yml`
- All services run locally
- Good for prototyping and testing

### Option 2: Kubernetes
- Deploy services as Kubernetes workloads
- Use Prometheus for metrics scraping
- Jaeger for distributed tracing

### Option 3: Managed Cloud Services
- Cloud PostgreSQL (AWS RDS, Google Cloud SQL)
- Cloud Redis (AWS ElastiCache, Google Memorystore)
- Cloud message queue (AWS SQS, Google Pub/Sub)
- Managed observability (Datadog, New Relic)

See [docs/patterns/edge-cloud-deployment/](docs/patterns/edge-cloud-deployment/) for deployment patterns.

## Performance Characteristics

### Agent Execution
- **Intent Detection**: ~50-200ms (edge)
- **Fraud Detection**: ~100-300ms (edge)
- **Trends Analysis**: ~500-2000ms (cloud, with inference)
- **Segmentation**: ~300-1500ms (cloud)

### Infrastructure
- **PostgreSQL Query**: <10ms (cached), <100ms (disk)
- **Redis Lookup**: <5ms
- **Message Queue Latency**: <100ms
- **Trace Export**: <50ms

See [Agentic SLOs](docs/patterns/predictability/agentic-slos.md) for detailed performance targets.

```python
# Pattern: Token Budgeting (see docs/patterns/predictability/token-budgeting.md)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add patterns, examples, or feedback.

## About This Project

This is one of six portfolio projects exploring architecture at scale:
- [Fintech Data Mesh](https://github.com/chakraview/fintech-data-mesh)
- [Zero-Trust Blueprint](https://github.com/chakraview/zero-trust-blueprint)
- [Real-Time Data Platform](https://github.com/chakraview/realtime-data-platform)
- [Enterprise Modernization](https://github.com/chakraview/enterprise-modernization)
- **Distributed Systems Patterns** (this project)
- [Developer Experience Paved Path](https://github.com/chakraview/devex-paved-path)

See [Chakraview Portfolio](https://naren-chakraview.github.io/) for overview.

## License

This project is provided for educational and reference purposes.
