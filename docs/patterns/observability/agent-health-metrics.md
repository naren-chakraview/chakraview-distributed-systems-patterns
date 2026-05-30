# Agent Health Metrics

## Problem Statement

How healthy is an agent? Is it meeting SLOs? Getting slower? Using more tokens? Producing lower-quality output? Health metrics answer these questions.

## Solution Approach

**Core Metrics:**

1. **Latency** — p50, p99, p99.9 per agent or agent pool
2. **Token consumption** — actual vs budgeted, per turn and per conversation
3. **Quality** — output validation pass rate, confidence scores
4. **Error rate** — timeouts, invalid outputs, exceptions per agent
5. **SLA compliance** — % of requests meeting SLO

**Dashboarding Pattern:**

```
Agent Health Dashboard (by agent_pool)
├─ Latency Percentiles (p50, p99, p99.9)
│  └─ RED: p99 > SLO threshold
├─ Token Budget Burn
│  ├─ Actual vs budgeted per turn
│  └─ RED: > 110% of budget
├─ Quality Metrics
│  ├─ Output validation pass rate
│  ├─ Average confidence
│  └─ RED: pass rate < 95%
├─ Error Rate
│  ├─ Timeout count
│  ├─ Invalid output count
│  └─ RED: error rate > 1%
└─ SLA Compliance
   ├─ % calls meeting end-to-end SLO
   └─ RED: < 95% compliant
```

**Per-Region Breakdown:**

Edge+cloud deployments track metrics per region:
- `latency_p99{region="us_east", agent_pool="edge"}`
- `token_budget_burn{region="us_east", agent_pool="edge"}`
- `quality_pass_rate{region="us_west", agent_pool="swarm"}`

**Alerting:**

- Latency p99 > 2× baseline = investigate
- Token burn > 120% budget = OOM risk
- Quality pass rate drops > 5% = data drift or bug
- Error rate > 1% = degradation

## When to Use

- Track these metrics for **all production agents**
- Use for **capacity planning** (growing token consumption?)
- Use for **SLA tracking** (compliance dashboard)
- Correlate with **code deployments** (did new version change metrics?)

## Trade-offs

| Metric | Cost | Insight | Cadence |
|--------|------|---------|---------|
| **Latency percentiles** | Low (histogram) | High (performance trend) | 1s |
| **Token counts** | Low (counter) | High (cost + budget tracking) | 1s |
| **Quality validation** | Medium (validation logic) | High (degradation detection) | 10s |
| **Error rate** | Low (counter) | Medium (knows something broke) | 1s |
| **SLA compliance** | Medium (aggregation) | Very high (business metric) | 1m |

**Recommendation:** Track all; alert on latency/error/SLA; use quality for learning.

## Example Alerts

```yaml
alerts:
  - name: edge_agent_latency_high
    rule: latency_p99{agent_pool="edge"} > 2000ms
    duration: 5m
    severity: warning

  - name: token_budget_exceeded
    rule: token_burn{agent_pool="swarm"} > 1.2
    duration: 1m
    severity: critical

  - name: quality_degradation
    rule: quality_pass_rate{region="us_east"} < 0.95
    duration: 10m
    severity: warning

  - name: slo_breach
    rule: sla_compliance < 0.95
    duration: 10m
    severity: critical
```

## Observability Hooks

**Queries:**
- "Which agent has highest latency p99?"
- "Which regions have lowest quality?"
- "Show SLA compliance over time"
- "Correlate latency spike with deployment"

**Metrics Export:**

Use Prometheus format:
```
# HELP agent_latency_seconds Agent invocation latency
# TYPE agent_latency_seconds histogram
agent_latency_seconds_bucket{agent="edge",region="us_east",le="1"} 100
agent_latency_seconds_bucket{agent="edge",region="us_east",le="5"} 450
agent_latency_seconds_bucket{agent="edge",region="us_east",le="+Inf"} 500

# HELP agent_tokens_consumed Agent tokens consumed
# TYPE agent_tokens_consumed counter
agent_tokens_consumed_total{agent="cloud",region="us_west"} 125000

# HELP agent_quality_pass Agent output quality pass rate
# TYPE agent_quality_pass gauge
agent_quality_pass{agent="swarm"} 0.97
```

## Framework Integration

**LangGraph:** Instrument spans with metrics:
```python
from prometheus_client import Histogram, Counter

latency = Histogram("agent_latency_seconds", ...)
tokens = Counter("agent_tokens", ...)

@app.get("/agent")
async def agent(request):
    with latency.labels(agent="edge").time():
        result = await run_agent(request)
    tokens.labels(agent="edge").inc(result.tokens)
    return result
```

**Temporal:** Export metrics from activity:
```python
@activity.run
async def run_agent(task):
    start = time.time()
    result = await agent.run(task)
    latency_ms = (time.time() - start) * 1000
    
    # Send to metrics backend
    metrics_client.record_latency(latency_ms)
    metrics_client.record_tokens(result.tokens)
    
    return result
```

## References

- [Agent Failure Modes](../../foundations/agent-failure-modes.md)
- [SLOs for Agentic Workloads](../predictability/agentic-slos.md)
- Prometheus: https://prometheus.io/
