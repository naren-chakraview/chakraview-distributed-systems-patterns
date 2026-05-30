# Distributed Tracing for Agent Calls

## Problem Statement

Agent calls span multiple hops: edge agent → cloud agent → database → response. Each hop has latency, errors, decisions. Debugging requires understanding: which inputs led to which outputs? Where did the delay occur? Which agent made the critical decision?

Distributed tracing provides end-to-end visibility: trace IDs link requests across services; spans represent operations; logs and metrics attach to traces.

## Solution Approach

**Core Concepts:**

- **Trace ID** — unique identifier for one user request flowing through system
- **Span** — one operation (agent invocation, tool call, LLM inference); has start/end time, status
- **Baggage** — context propagated with trace: agent pool, region, priority, vector clock
- **Span attributes** — key-value metadata: input tokens, output tokens, decision, model used

**Instrumentation Pattern:**

```
User request → trace_id = uuid()
  ├─ edge_agent span (input_tokens=100, output_tokens=150)
  │   ├─ baggage: {agent_pool: "edge_us_east", vector_clock: {A:1}}
  │   └─ child span: send_to_cloud (latency=45ms)
  │
  ├─ cloud_agent span (input_tokens=200, output_tokens=300)
  │   ├─ child span: run_inference (latency=1200ms, model="claude-3-sonnet")
  │   └─ child span: run_tool (latency=50ms, tool="database_query")
  │
  └─ edge_executor span (status=success)
```

**Implementing:**

1. Generate trace_id at request entry point (edge agent)
2. Propagate trace_id + baggage in every message (headers, function args, queue messages)
3. Create span for each agent invocation (start → log events → end)
4. Attach attributes (tokens, decision, model, latency)
5. Export traces to tracing backend (Jaeger, DataDog, etc.)

**Baggage Contents:**

- Agent pool (edge, cloud, swarm)
- Edge region (us-east, eu-west, etc.)
- Priority (critical, normal, batch)
- Vector clock (causality tracking)
- User context (user_id, tenant_id)

## When to Use

- Always instrument agent calls in production
- Trace every invocation (if sampling needed, sample at backend, not agent)
- Increase baggage in slow/failed requests (for better debugging)
- Lighter tracing in stable, fast paths

## Trade-offs

| Approach | Overhead | Debug Visibility | Cost |
|----------|----------|-----------------|------|
| **No tracing** | None | Poor (logs only) | Low |
| **Basic tracing** (trace_id only) | Low (< 1% latency) | Medium (which requests, not why) | Low |
| **Full tracing** (spans + baggage + attributes) | Medium (2-5% latency) | High (full causality) | Medium |
| **Per-token tracing** | High (10%+ latency) | Very high (token-level decisions) | High |

**Recommendation:** Start with basic tracing (trace_id); upgrade to full tracing for slow paths; use per-token tracing only for debugging.

## Observability Hooks

**Metrics:**
- Trace completion rate (% of requests traced)
- Span count per request (detect long chains)
- Trace latency distribution (p50, p99)
- Baggage cardinality (unique agent_pools, regions, etc.)

**Queries:**
- "Show all spans for trace_id X"
- "What was edge agent decision in trace Y?"
- "Which traces experienced timeout in cloud agent?"
- "Compare latency distribution across edge regions"

## Example: End-to-End Trace

```json
{
  "trace_id": "abc123",
  "spans": [
    {
      "name": "edge_agent",
      "start_time": "2026-05-29T10:00:00Z",
      "duration_ms": 200,
      "attributes": {
        "agent_pool": "edge_us_east",
        "input_tokens": 150,
        "output_tokens": 75,
        "decision": "forward_to_cloud"
      },
      "baggage": {
        "vector_clock": {"edge": 5, "cloud": 2},
        "priority": "normal"
      }
    },
    {
      "name": "cloud_agent",
      "start_time": "2026-05-29T10:00:00.200Z",
      "duration_ms": 1500,
      "attributes": {
        "agent_pool": "cloud",
        "input_tokens": 200,
        "output_tokens": 300,
        "model": "claude-3-sonnet",
        "decision": "approve"
      },
      "child_spans": [
        {
          "name": "run_inference",
          "duration_ms": 1200,
          "model": "claude-3-sonnet"
        }
      ]
    }
  ]
}
```

## Framework Integration

**LangGraph:** Use LangGraph's built-in tracing + custom attributes:
```python
from langchain_core.tracers import LangChainTracer

tracer = LangChainTracer(project_name="agents")
# Traces automatically; add custom attributes via context
```

**Temporal:** Workflow history is implicit trace; export to tracing backend:
```python
@workflow.run
async def agent_workflow(task):
    # Temporal records this in workflow history
    result = await activities.run_agent(task)
    return result
```

## Code References

### Reference Implementation

**Vector Clock (Causality Tracking):**
- File: `reference-implementations/shared/python/vector_clock.py`
- Class: `VectorClock` — tracks causal relationships
- Methods:
  - `increment(agent_id)` — increment clock for this agent
  - `merge(other)` — merge incoming clock (implements happened-before relation)
  - `to_dict()` — serialize for propagation in messages

**Agent Base with Trace Support:**
- File: `reference-implementations/shared/python/agent_base.py`
- Method: `set_trace_id()` (lines 60-69) — sets trace ID for correlation
- Method: `set_vector_clock()` (lines 71-80) — merges incoming vector clock

**Structured Logging:**
- File: `reference-implementations/shared/python/logging.py`
- Class: `StructuredLogger` — attaches trace ID to all logs
- Methods:
  - `set_trace_id()` — sets trace ID for request context
  - `set_vector_clock()` — embeds vector clock in logs

### Tests

**Integration Tests:**
- File: `tests/integration/test_full_pipeline.py`
- Test: `test_trace_id_correlation()` (lines 240-255)
  - Documents trace ID propagation interface
  - Shows how agents would receive and use trace IDs

- Test: `test_vector_clock_propagation()` (lines 68-110)
  - Verifies vector clocks increment correctly
  - Tests clock merging across agents
  - Validates causality tracking

**Fixtures:**
- File: `tests/conftest.py`
- VectorClock class: Lines 35-52 (mock implementation)
- Result dataclasses: Lines 50+ (include vector_clock field)

### Infrastructure

**Jaeger Backend:**
- File: `examples/local-dev/docker-compose.yml`
- Service: jaeger (lines for jaeger-all-in-one)
- Port: 6831 (UDP for spans), 16686 (UI)

**Demo:**
- File: `examples/pattern-demos/demo_tracing.py`
  - Shows how to instrument agents with tracing
  - Demonstrates trace visualization in Jaeger

## References

- [Understanding Model Decisions](understanding-decisions.md)
- [Causality & Ordering](../../foundations/causality-and-ordering.md)
- [Multi-Agent Coordination](../integration/multi-agent-coordination.md)
- OpenTelemetry: https://opentelemetry.io/
