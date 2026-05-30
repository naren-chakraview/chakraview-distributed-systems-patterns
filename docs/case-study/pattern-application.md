# Case Study: Pattern Application & Failure Scenarios

## How Patterns Apply

### Observability
- **Distributed Tracing:** Trace each user request from edge intent detection → cloud segmentation → dashboard
- **Understanding Decisions:** Log why edge agent classified as "buying" vs "browsing"; confidence 90%
- **Logging Strategies:** Structured logs with idempotency keys for retries
- **Agent Health Metrics:** Track latency_p99, token burn, accuracy per agent

### Predictability
- **Context Window Management:** Cloud agent uses sliding window for user history (keep recent 50 users)
- **Token Budgeting:** Edge budgets 200 tokens/request; cloud budgets 3K tokens/request
- **Behavior Degradation:** If cloud latency > 5s, edge returns cached insights (graceful)
- **SLOs:** 95% of end-to-end requests < 500ms; 95% accuracy

### Resource Allocation
- **Fair Queuing:** VIP users (high-value) get 40% of cloud GPU; regular users get 50%; batch get 10%
- **Reservation vs. Burst:** Reserve 30% for real-time; 70% for batch backtest
- **Token Budgeting:** Monitor spend; alert if > 110% of budget

### Failure Recovery
- **Idempotency:** Each user event has idempotency_key = "user:alice:event:12345:retry:1"
- **Checkpointing:** Cloud saves aggregated state every 100 events (to tolerate restarts)
- **Network Partitions:** Edge queue handles store → cloud disconnection; replays on reconnect
- **ACID Guarantees:** Backtest saga: acquire lock → test strategy → commit results → release lock

### Edge+Cloud Deployment
- **Agent Placement:** Edge = lightweight (intent, fraud); Cloud = powerful (segmentation, trends)
- **Asynchronous Coordination:** Events queue batches; not request-response
- **Local vs. Remote Inference:** Edge inference < 100ms; cloud inference < 5s
- **Edge State Consistency:** User history eventually syncs to cloud (latency acceptable)
- **Partition Handling:** Edge queue persists; when cloud recovers, replay batches

### Integration
- **Single-Agent at Scale:** Edge Intent Agent replicated across 1000 stores; load balanced
- **Multi-Agent Coordination:** Intent → Fraud → Segmentation (chain delegation)
- **Agent Swarms:** 100 swarm agents backtest in parallel; aggregate results (voting)
- **Hierarchical:** Stores → regional aggregators → cloud (implicit hierarchy)

## Failure Scenarios

### Scenario 1: Cloud Inference Timeout

**Situation:** Cloud Agent 1 (segmentation) times out; user waiting for insight.

**Pattern Response:**
1. **Timeout detection:** p99 latency spike (from 5s → 30s)
2. **Circuit breaker:** After 5 timeouts, stop sending new requests (fail fast)
3. **Graceful degradation:** Return cached segmentation (24h old) + warning
4. **Recovery strategy:** Retry with reduced max_tokens; fallback to simpler model
5. **SLO impact:** Accuracy drops to 85% (cached data); still meets 95% uptime SLO

**Metrics:**
```
Before: latency_p99=5s, accuracy=95%
During: latency_p99=100ms (cached), accuracy=85%
After: latency_p99=5s, accuracy=95% (normal resumed)
Error budget burn: 0.5% (partial accuracy loss)
```

### Scenario 2: Network Partition (Edge Isolated)

**Situation:** Store internet down for 2 hours; edge agents isolated.

**Pattern Response:**
1. **Detection:** Health check timeout; mark cloud as unavailable
2. **Edge fallback:** Local queue buffers events (can store 100K events)
3. **Local insight generation:** Edge agents run on cached models; return local-only insights
4. **Async queue:** Store everything in queue
5. **Reconnection:** When internet restored, replay queue to cloud
6. **State reconciliation:** Cloud merges local events with other stores

**SLO Impact:**
- During outage: 0% cloud insights (local only) = SLO breach
- Error budget: 2 hours / (730 hours/month) = 0.27% burn
- After recovery: Full functionality restored

### Scenario 3: Cloud Agent Crashes (Out of Memory)

**Situation:** Cloud Agent 1 (segmentation) runs out of memory; crashes on large batch.

**Pattern Response:**
1. **Idempotency:** Batch had idempotency_key; retry is safe (will return cached result)
2. **Checkpointing:** Cloud had saved state before crash; recover from checkpoint
3. **Recovery strategy:** Retry with smaller batch size (500 → 250 users); use simpler model
4. **ACID guarantee:** Saga pattern ensures: if Agent 1 fails, results not persisted
5. **Fallback:** Use previous segmentation result (old, but safe)

**Timeline:**
```
T=0s: Crash detected
T=1s: Failover to backup instance + load checkpoint
T=5s: Retry with smaller batch → succeeds
T=6s: Results available; SLO met (< 10s latency)
Error budget: 6s / 10s = 60% budget for this request (high but acceptable)
```

### Scenario 4: Token Budget Exceeded

**Situation:** Cloud Agent (segmentation) uses 5K tokens per request instead of budgeted 3K.

**Pattern Response:**
1. **Detection:** Token accounting shows 5K usage
2. **Alert:** "Token budget exceeded; investigate immediately"
3. **Observation:** Reasons for overage:
   - User history (50 users) requires 60 tokens (was budgeted 40)
   - Model is more verbose than expected
4. **Graceful degradation:** Reduce user history size to 30 users; trim output
5. **Cost impact:** 3K → 5K = 67% increase per request; scale to 100K RPS = 200M extra tokens/day
6. **Action:** Optimize model or reduce batch size

**Prevention for next time:**
- Reserve 4K tokens (instead of 3K) for cloud agent
- More conservative budgeting going forward

## Lessons Learned

1. **Edge for latency, cloud for accuracy** — worked as designed
2. **Async queuing is critical** — handled network partition gracefully
3. **SLOs guide decisions** — when at 95% uptime SLO, failures acceptable if within error budget
4. **Checkpointing saves tokens** — recovering from checkpoint 10× cheaper than re-running
5. **Fallback chains enable reliability** — graceful degradation better than failure

