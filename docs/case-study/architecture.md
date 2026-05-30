# Case Study: Detailed Architecture

## Component Breakdown

### Edge Tier (Stores)

**Edge Agent 1: Intent Detection**
- Input: User behavior stream (clicks, searches, cart additions)
- Model: Small distilled model (2B params, 8K token context)
- Latency SLO: < 50ms (p99)
- Output: Intent classification (browse, buy, research, complain)

**Edge Agent 2: Fraud Detection**
- Input: Transaction details (amount, merchant, user history)
- Model: Small classifier (1B params, 4K token context)
- Latency SLO: < 100ms (p99)
- Output: Risk score (0-1), decision (approve/flag/block)

**Queue (SQS-like)**
- Buffers events from edge agents
- Sends batches to cloud every 5 seconds or 1000 events
- Handles network partitions (local queue survives outage)

### Cloud Tier

**Event Aggregator**
- Receives batches from 1000+ stores
- Deduplicates (same event from multiple sources?)
- Enriches (add context: holiday, weather, promotion)
- Queues for processing

**Cloud Agent 1: Customer Segmentation**
- Input: Aggregated user behavior (intent + fraud risk + purchase history)
- Model: Large transformer (70B params, 128K token context)
- Latency SLO: < 5 seconds
- Output: Segment classification (VIP, loyal, at-risk, inactive)

**Cloud Agent 2: Trend Detection**
- Input: Time-series aggregated sales, fraud patterns, intent shifts
- Model: Large timeseries model (50B params)
- Latency SLO: < 10 seconds
- Output: Trends (rising/falling/stable), confidence score

**Agent Swarm: Backtest**
- 100 swarm agents in parallel
- Each agent backtests on 1% of historical data
- Aggregates results: which strategies were profitable?
- Latency: batch job (no SLO, runs async)

**Decision Agent**
- Synthesizes insights from cloud agents + swarms
- Generates user-facing insights: "Customers buying home goods more this week"
- Ranks by impact + confidence
- Returns top 5 insights per user

### Data Flow

```
User browsing → Event (click, add-to-cart)
  ↓
Edge Agent 1 (intent)
  Intent: "buying" (90% confidence)
  ↓
Edge Agent 2 (fraud)
  Risk: 0.05 (approve)
  ↓
Queue batches every 5s
  [intent, risk, user_id, timestamp] × 1000 events
  ↓
Cloud Aggregator
  Group by user → [intents], [risks]
  ↓
Cloud Agent 1 (segmentation)
  User segment: "VIP" (high purchase frequency + intent=buying)
  ↓
Cloud Agent 2 (trends)
  Trend: "home goods trending +30% this week"
  ↓
Decision Agent
  Insight: "VIPs buying home goods; recommend category"
  ↓
User dashboard → "Try our new home goods collection"
```

## Resource Budget

### Edge Agent 1 (Intent)
```
Total context: 8K tokens
├─ System prompt: 500 (reserved)
├─ User input: 100 (actual)
├─ User history: 2000 (allocated)
├─ Reserved output: 500
└─ Free: 4900

Actual per request: ~200 tokens (input 100 + output 50 + overhead)
Throughput: 1000 concurrent users × 100 RPS = 100K RPS
Token consumption: 100K × 200 = 20M tokens/sec
```

### Cloud Agent 1 (Segmentation)
```
Total context: 128K tokens
├─ System prompt: 2K (reserved)
├─ Aggregated data: 50K (1000 users × 50 tokens each)
├─ History: 40K (reference data)
├─ Reserved output: 5K
└─ Free: 31K

Actual per request: ~3K tokens (input 50 + output 100 + reasoning overhead)
Throughput: 100 RPS (batched)
Token consumption: 100 × 3K = 300K tokens/sec
```

## SLOs

```yaml
slos:
  - name: "intent_detection_latency"
    metric: "latency_p99"
    threshold: "50ms"
    target: "99%"
    
  - name: "fraud_detection_latency"
    metric: "latency_p99"
    threshold: "100ms"
    target: "99%"
    
  - name: "end_to_end_latency"
    metric: "latency_p99"
    threshold: "500ms"  # edge + queue + cloud + network
    target: "95%"
    
  - name: "accuracy"
    metric: "validation_pass_rate"
    threshold: "95%"
    target: "99%"
    
  - name: "availability"
    metric: "uptime"
    threshold: "99.9%"
    target: "100%"
```

## Scaling Plan

| Phase | Users | RPS | Infrastructure |
|-------|-------|-----|-----------------|
| Phase 1 | 1000 | 100 | 10 stores, 2 cloud GPU |
| Phase 2 | 10K | 1K | 100 stores, 10 cloud GPU |
| Phase 3 | 100K | 10K | 1000 stores, 50 cloud GPU |
| Phase 4 | 1M | 100K | 10000 stores, 200 cloud GPU |
