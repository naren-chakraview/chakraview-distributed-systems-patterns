# AI Analytics Engine — Reference Implementation

A modular, production-grade implementation of the AI Analytics Engine case study, demonstrating all 35 distributed systems patterns from the [Distributed Systems for Agentic Workloads](../../) documentation.

## Quick Start

```bash
docker-compose -f examples/local-dev/docker-compose.yml up
```

## Structure

- **shared/** — Protocol Buffer definitions and base classes
- **edge-agents/** — Intent detection and fraud detection agents
- **cloud-agents/** — Segmentation and trends agents
- **swarm/** — Backtest processor swarm
- **queue/** — Async coordination service (Go)
- **observability/** — Distributed tracing service (Go)
- **orchestration/** — Workflow orchestrator (Go + Python)
- **examples/** — Deployment configs and demos

## Pattern Demonstrations

Each module includes code comments that reference specific patterns:

```python
# Pattern: Token Budgeting (see docs/patterns/predictability/token-budgeting.md)
```

See [PATTERN_LINKS.md](PATTERN_LINKS.md) for a complete mapping of code examples to documentation.

## Testing

```bash
make test
```

## Building

```bash
make proto  # Generate gRPC code
make build  # Compile Go binaries
```
