# Logging Strategies for Non-Deterministic Systems

## Problem Statement

Logging agent activity is tricky. Logs grow huge (one log per token?). But without detail, debugging is impossible. How do we log enough to debug without logging too much?

## Solution Approach

**Structured Logging (not free-form text):**

```json
{
  "timestamp": "2026-05-29T10:00:00Z",
  "trace_id": "abc123",
  "agent_id": "cloud_inference",
  "event": "inference_started",
  "input_tokens": 150,
  "context_tokens": 250,
  "model": "claude-3-sonnet",
  "temperature": 0.7,
  "seed": 12345
}
```

Benefits: queryable, parseable, consistent format.

**Log Levels for Agents:**

- **DEBUG** (verbose) — every token generated; not for production
- **INFO** (standard) — agent invocation, decision, token count; use in production
- **WARN** (alerts) — budget exceeded, timeout approaching, low confidence
- **ERROR** — failures, invalid output, exception

**Sampling & Truncation:**

- Log every agent invocation (decision checkpoints)
- Sample token stream (every 100th token, or every decision point)
- Truncate long outputs (log first 1000 chars + "...")
- For retries: log with idempotency key (detect retries in logs)

**Capturing Non-Determinism:**

```json
{
  "event": "inference_started",
  "model_version": "claude-3-sonnet-2025-05-01",
  "temperature": 0.7,
  "seed": 42,  // If present, enables replay
  "max_tokens": 500,
  "sampler": "nucleus_p=0.9"
}
```

When seed/sampler available, log them. Enables exact replay if needed.

**Idempotency Keys in Logs:**

```json
{
  "event": "workflow_step",
  "idempotency_key": "user:alice:expense:12345:retry_2",
  "step": "approval",
  "attempt": 2,
  "retry_reason": "timeout"
}
```

Queries: "show all retries for this task" or "detect duplicate execution."

## When to Use

- Always use structured logging
- Always log agent invocations (entry/exit + decision)
- Log token counts + model parameters
- Sample token stream (not every token)
- Log only failure root causes; omit success path noise

## Trade-offs

| Strategy | Log Volume | Debug Visibility | Storage Cost |
|----------|-----------|-----------------|--------------|
| **Log every token** | Very high (10-100x normal) | Very high (token-level) | $$$$ |
| **Log decisions only** | Low (10-100 bytes per invocation) | Medium (know decision, not why) | $ |
| **Log + sample stream** | Medium (1-10KB per invocation) | High (decision + sample of reasoning) | $$ |
| **Structured + queries** | Medium | High (queryable; easy filtering) | $$ |

**Recommendation:** Structured logging + log decisions + sample token stream for complex decisions.

## Observability Hooks

**Queries:**
- "Show all agent invocations where output_tokens > budget"
- "Group by agent_pool; count of each log level"
- "Find all retries; show idempotency_key duplicates"
- "Which agents have high ERROR rate?"

**Metrics:**
- Error rate per agent
- Retry frequency
- Average log volume (MB/hour)

## Example: Multi-Turn Conversation Logs

```json
[
  {
    "turn": 1,
    "event": "user_input",
    "message": "Summarize Q3 sales",
    "token_count": 8
  },
  {
    "turn": 1,
    "event": "agent_invocation",
    "agent": "edge_analytics",
    "input_tokens": 250,
    "context_tokens": 100,
    "model": "claude-3-sonnet"
  },
  {
    "turn": 1,
    "event": "agent_response",
    "agent": "edge_analytics",
    "output_tokens": 145,
    "decision": "insufficient_context_forward_to_cloud",
    "confidence": 0.92
  },
  {
    "turn": 1,
    "event": "agent_invocation",
    "agent": "cloud_analytics",
    "input_tokens": 500,
    "database_query": "SELECT SUM(sales) FROM orders WHERE quarter=3",
    "query_latency_ms": 245
  },
  {
    "turn": 1,
    "event": "agent_response",
    "agent": "cloud_analytics",
    "output_tokens": 320,
    "decision": "return_to_edge",
    "output_preview": "Q3 sales: $12.5M, up 15% vs Q2..."
  }
]
```

## References

- [Distributed Tracing](distributed-tracing.md)
- [Causality & Ordering](../../foundations/causality-and-ordering.md)
