# SLOs for Agentic Workloads

## Problem Statement

SLOs (Service Level Objectives) define what's acceptable: "99% of requests complete within 2 seconds." But agents are probabilistic. Same request sometimes completes in 1s, sometimes 3s. How do we define SLOs for non-deterministic systems?

## Solution Approach

**SLO Definition for Agents:**

Separate concerns:

1. **Deterministic SLOs** — latency, availability (same as traditional systems)
2. **Quality SLOs** — output quality, confidence, correctness (agent-specific)
3. **Resource SLOs** — token usage, memory (agent-specific)

**Example SLOs:**

```yaml
slos:
  - name: "end_to_end_latency"
    metric: "latency_p99"
    threshold: "2000ms"
    window: "1 hour"
    target: "99%"  # 99% of requests meet SLO
    
  - name: "output_quality"
    metric: "validation_pass_rate"
    threshold: "95%"  # 95% of outputs pass validation
    window: "1 hour"
    target: "99%"  # 99% of hours meet this
    
  - name: "token_efficiency"
    metric: "actual_tokens / budgeted_tokens"
    threshold: "1.1"  # Allow 10% overage
    window: "1 hour"
    target: "99%"  # 99% of hours within budget
```

**Error Budget:**

If SLO is 99% uptime / 99% latency, error budget is 1%:
- 1% of 730 hours/month = 7.3 hours
- You can afford 7.3 hours of downtime/SLA breach without violating SLO
- Track burn rate: if burned > 10%/day, alert and stop deployments

**Probabilistic SLOs:**

For non-deterministic outputs:

```
Quality SLO: "95% of outputs pass validation"
means: of 1000 outputs, ≥ 950 should be valid

Latency SLO (probabilistic): "p99 latency < 2s"
means: 99% of requests complete within 2s
(1% can take longer; this is probabilistic acceptance)
```

## When to Use

- Define latency SLOs like traditional services (p99, availability)
- Add quality SLOs specific to your agent (output validation rate, confidence threshold)
- Add resource SLOs (token budgets, memory usage)
- Use error budgets to manage deployments (don't deploy if error budget depleted)

## Trade-offs

| SLO Type | Measurability | Business Value | Complexity |
|----------|---------------|----------------|-----------|
| **Latency** | High (direct measurement) | High | Low |
| **Availability** | High (up/down) | High | Low |
| **Quality** | Medium (validation rules) | High | Medium |
| **Confidence** | Medium (model-dependent) | Medium | Medium |
| **Resource** | High (direct measurement) | Medium (cost control) | Low |

**Recommendation:** Define latency + quality SLOs; track error budget; use error budget to gate deployments.

## Burn Rate Alerts

```yaml
alerts:
  - name: "slo_burn_high"
    rule: "error_budget_burn_rate > 10% / day"
    duration: "5 minutes"
    action: "pause deployments"
    
  - name: "slo_breach_imminent"
    rule: "error_budget_remaining < 20%"
    duration: "1 hour"
    action: "notify oncall"
```

## References

- [Agent Health Metrics](../observability/agent-health-metrics.md)
- Beyer, B., et al. (2016). "Site Reliability Engineering"
