# Zero Trust for Agents

## Title

Zero Trust for Agents: Identity, Capability, and Delegation in Distributed Agent Systems

## Problem Statement

Contemporary distributed systems have two well-established identity classes: **human identities** managed by IAM systems and **service identities** managed by SPIFFE/SPIRE. A third class—**agent identities**—has emerged in agentic systems with fundamentally different characteristics.

Agents are dynamically spawned, short-lived entities with ephemeral lifespans (seconds to minutes) and capability sets that vary per instantiation. Unlike services, agents may be created at runtime in response to user requests or cascading orchestration, may delegate trust to sub-agents (forming delegation chains), and often operate with sub-minute time-to-live (TTL) windows. Some agents run on resource-constrained edge devices, others in controlled cloud environments, and still others within orchestration layers—each tier has distinct trust requirements.

The security challenge is three-fold: (1) **identity verification** across tiers and delegation chains, (2) **capability enforcement** where agents must be restricted to their designated permissions, and (3) **revocation and expiry** management in systems where TTLs are measured in seconds and agents may disappear without notice.

Existing zero-trust frameworks (e.g., the chakraview-zero-trust-blueprint) were designed for stable service identities. They assume identities are long-lived, registered in advance, and follow a single trust vector. Agent systems violate all three assumptions.

Additionally, **trust & byzantine.md** addresses agent **output verification**—how to validate that a model's claims are sound. This document addresses agent **identity and authorization**—verifying that the agent making the request is permitted to do so.

## Solution Approach

We adopt a **three-plane model** adapted from zero-trust principles but specialized for agent identity:

### Plane 1: Identity

**AgentIdentity tokens** are minted at spawn time by the orchestrator or spawning agent. Each token encodes:

- **agent_id**: Globally unique identifier
- **agent_type**: Categorical identity (orchestrator, cloud_agent, edge_agent, sub_agent, etc.)
- **trust_tier**: One of {orchestrator, cloud_agent, edge_agent}
- **capabilities**: Set of permitted actions (e.g., ["spawn_sub_agent", "query_api", "log_event"])
- **issuer**: Identity of the entity that created this agent
- **issued_at, expires_at**: Unix timestamps; TTLs vary by tier:
  - **Edge agents**: 30 seconds (devices may go offline; re-spawn on reconnection)
  - **Cloud agents**: 120 seconds (stable compute; longer safe operations)
  - **Orchestrators**: 300 seconds (coordination overhead; infrequent spawning)
- **parent_agent_id**: For delegation chains; NULL if spawned by human/system

**Token format (production)**: SPIFFE JWT SVIDs issued by SPIRE workload API. In development or constrained environments, HMAC-signed tokens with the above claims.

### Plane 2: Tier Authorization

Three tiers with hierarchical trust:

```
orchestrator (highest)
  ↓ can spawn
cloud_agent (medium)
  ↓ can spawn
edge_agent (lowest)
  ↓ cannot spawn further
```

**allowed_caller_tiers policy**: Each call target (API endpoint, agent spawn, sub-agent delegation) specifies which tiers may invoke it.

Example:
```yaml
spawn_sub_agent:
  allowed_caller_tiers: [orchestrator, cloud_agent]  # edge cannot spawn

query_cloud_api:
  allowed_caller_tiers: [orchestrator, cloud_agent]  # edge calls cloud through proxy

log_edge_metric:
  allowed_caller_tiers: [edge_agent, cloud_agent, orchestrator]  # any tier can log
```

### Plane 3: Capability Policy

Each agent type has a static set of **allowed_capabilities**. At authorization time, the request specifies which capability it requires; the agent must possess that capability.

```yaml
agent_types:
  edge_agent:
    allowed_capabilities: [log_metric, sync_state, query_local_cache]
  cloud_agent:
    allowed_capabilities: [log_metric, query_api, spawn_sub_agent, sync_state]
  orchestrator:
    allowed_capabilities: [spawn_sub_agent, escalate_alert, revoke_agent]
```

A request succeeds if:
```
requested_capabilities ⊆ agent.capabilities
```

### Chain Depth Enforcement

Delegation chains are tracked via **caller_chain**: a list of agent IDs that led to the current request.

```
user/orchestrator → agent-A → agent-B → agent-C (current)
caller_chain = [orchestrator, agent-A, agent-B]
chain_depth = 3
```

**max_delegation_depth** (default: 5) prevents runaway recursion:

```python
if chain_depth >= max_delegation_depth:
    raise AuthzError("max delegation depth exceeded")
```

### Production Deployment

1. **SPIRE integration**: Agents request SPIFFE SVIDs from the SPIRE workload API at spawn time. SPIRE mints a JWT with embedded claims (agent_type, trust_tier, parent_agent_id).
2. **Offline-first fallback**: In edge/offline scenarios, agents carry HMAC-signed tokens issued at spawn. The orchestrator pre-shares the HMAC secret.
3. **Token refresh**: Long-lived agents (cloud_agent > 120s) request fresh tokens from a token service before expiry.
4. **Revocation**: Orchestrator publishes revocation lists (agent IDs to deny). Leaf agents poll or subscribe to revocation feeds.

## When to Use

Apply Zero Trust for Agents when:

- **Agents call external APIs** and you need audit trails and per-call authorization
- **Agents spawn sub-agents** and you must prevent unauthorized spawning or capability escalation
- **Cross-tier communication** occurs (e.g., edge agents call cloud services)
- **Trust boundaries exist** (e.g., multi-tenant deployments, untrusted partner models)
- **Audit and compliance** require call-level signatures and proof of authorization

**Not needed** for:

- Single-agent systems with no spawning
- Fully trusted environments (e.g., internal R&D sandbox)
- Systems where output verification (trust-and-byzantine) alone is sufficient

## Trade-offs

| Concern | With Zero Trust | Without |
|---------|-----------------|---------|
| **Security** | Independent authz per call; compromised agent cannot exceed its capabilities | Compromised agent has all parent's permissions; lateral movement possible |
| **Latency** | +1–5ms per call for token validation (HMAC check) or SPIFFE SVID lookup | None |
| **Complexity** | Requires policy YAML, token lifecycle mgmt, secret rotation automation | None; implicit trust in agent process |
| **Auditability** | Signed audit records for every call; forensics trivial | No call-level audit; forensics requires log correlation |
| **Operational overhead** | SPIRE deployment, token service, revocation feed infrastructure | None |

## Observability Hooks

### Metrics

- **validation_failures_total** (counter, by reason: expired, no_capability, exceeded_chain_depth, invalid_signature)
- **chain_depth_histogram** (distribution of caller_chain lengths; alert if approaching max)
- **ttl_remaining_seconds** (gauge, per agent_id; alert if < 10s for active agents)
- **authz_decisions_total** (counter, by decision: allow, deny; by tier, by action)

### Logs

Every **EnforcementResult** is logged as JSON for audit/forensics:

```json
{
  "timestamp": "2026-05-29T10:30:45.123Z",
  "enforcement_id": "enf-abc123",
  "caller": {
    "agent_id": "cloud-agent-xyz",
    "agent_type": "cloud_agent",
    "trust_tier": "cloud_agent",
    "parent_agent_id": "orchestrator-abc"
  },
  "target_action": "spawn_sub_agent",
  "decision": "ALLOW",
  "reason": "tier authorized, capability present, chain_depth=2 < max=5",
  "chain_depth": 2,
  "ttl_remaining_seconds": 87,
  "validation_latency_ms": 2.3
}
```

### Alerts

- **Spike in DENY decisions** (>2σ from baseline): possible misconfiguration or attack
- **chain_depth approaching max**: potential runaway delegation
- **Token expiry storms**: agents expiring en masse; possible clock skew or mass orchestrator failure

## Example: 4-Hop Delegation Chain

**Scenario**: A user request triggers an analytics job, which spawns a cloud coordinator, which spawns edge sensors on two devices.

```
┌─────────────────────────────────────────────────────────────────┐
│ User / Orchestrator (orch)                                       │
│   Created: t=0, Expires: t=300s, Trust Tier: orchestrator        │
│   Capabilities: [spawn_sub_agent, escalate_alert, revoke_agent]  │
└─────────────────────────────────────────────────────────────────┘
       │
       │ spawn_sub_agent call (chain_depth=0)
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ Cloud Agent (cloud-xyz)                                          │
│   Created: t=5, Expires: t=125s, Trust Tier: cloud_agent         │
│   Capabilities: [log_metric, query_api, spawn_sub_agent]         │
│   Parent: orchestrator-abc, Chain: [orch]                        │
└─────────────────────────────────────────────────────────────────┘
       │
       │ spawn_sub_agent call (chain_depth=1)
       ├─────────────────────────────────┬──────────────────────────┐
       ▼                                 ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│ Edge Agent (edge-dev1)    │  │ Edge Agent (edge-dev2)    │
│ Created: t=10            │  │ Created: t=10             │
│ Expires: t=40 (30s TTL)  │  │ Expires: t=40 (30s TTL)   │
│ Trust Tier: edge_agent   │  │ Trust Tier: edge_agent    │
│ Capabilities:            │  │ Capabilities:             │
│  [log_metric,            │  │  [log_metric,             │
│   sync_state]            │  │   sync_state]             │
│ Parent: cloud-xyz        │  │ Parent: cloud-xyz         │
│ Chain: [orch, cloud-xyz] │  │ Chain: [orch, cloud-xyz]  │
│                          │  │                           │
│ EnforcementResult @ log: │  │ EnforcementResult @ sync: │
│ ──────────────────────── │  │ ──────────────────────── │
│ caller: edge-dev1        │  │ caller: edge-dev2         │
│ action: log_metric       │  │ action: sync_state        │
│ decision: ALLOW          │  │ decision: ALLOW           │
│ chain_depth: 2           │  │ chain_depth: 2            │
│ ttl_remaining: 27s       │  │ ttl_remaining: 25s        │
│ latency: 1.2ms           │  │ latency: 1.1ms            │
└──────────────────────────┘  └──────────────────────────┘

At t=45s (5s after edge agent expiry):
  → Edge agents attempt to log → ValidationError: token expired
  → Cloud coordinator detects failure, requests re-spawn from orchestrator
  → New edge agents created with fresh 30s TTL
```

**Call sequence with EnforcementResult logs**:

```
[t=5] Orchestrator → Cloud Agent spawn
  EnforcementResult(caller=orch, action=spawn_sub_agent, decision=ALLOW, chain_depth=0)

[t=10] Cloud Agent → Edge Device 1 spawn
  EnforcementResult(caller=cloud-xyz, action=spawn_sub_agent, decision=ALLOW, chain_depth=1)
  → Succeeds (cloud_agent tier allowed to spawn)

[t=12] Edge Agent (dev1) → log_metric
  EnforcementResult(caller=edge-dev1, action=log_metric, decision=ALLOW, chain_depth=2)
  → Succeeds (edge_agent capability includes log_metric)

[t=45] Edge Agent (dev1) → log_metric (AFTER EXPIRY)
  EnforcementResult(caller=edge-dev1, action=log_metric, decision=DENY, 
    reason=token_expired, ttl_remaining=-5s, chain_depth=2)
  → Fails; cloud coordinator handles retry logic
```

## Failure Scenarios

### 1. Token Expiry Mid-Chain

**Scenario**: A cloud agent spawns an edge agent at t=10 with a 30s TTL (expires at t=40). At t=38, the edge agent sends a log_metric call. At t=42, it sends another call, but the token has expired.

**Recovery**:
- The failed call returns a 401 Unauthorized with reason "token_expired"
- The cloud coordinator catches this, increments a retry counter
- After 2–3 failed attempts, the coordinator requests a re-spawn from the orchestrator
- A fresh edge agent is created and the work resumes

**Observability**: The orchestrator's metrics show a spike in `validation_failures_total{reason="expired"}`, and the cloud agent logs the re-spawn. Alerts fire if re-spawn rate exceeds threshold.

### 2. Registry Out of Sync

**Scenario**: A new agent type (ai_auditor) is added to the system, but the policy registry has not been updated with its allowed_capabilities or allowed_caller_tiers.

**Scenario**: Orchestrator attempts to spawn an ai_auditor agent. The policy lookup finds no entry for ai_auditor type.

**Recovery**:
- The spawn is blocked with a 403 Forbidden: "unknown agent type: ai_auditor"
- The operator must add the agent type to the policy registry and reload it (or hot-swap)
- Once the policy is in place, spawn succeeds

**Prevention**: CI/CD validation ensures all new agent types are registered before code merge.

### 3. Chain Depth Runaway

**Scenario**: A buggy orchestrator agent has a loop that spawns sub-agents without bound: A → B → C → D → ... At some depth N = max_delegation_depth (default 5), the system stops accepting new spawns.

**Recovery**:
- Spawn request at depth N returns 403 Forbidden: "max delegation depth exceeded"
- The orchestrator's error handling catches this and stops spawning
- Alert fires: "chain_depth_histogram p99 > threshold or chain_depth == max"
- On-call engineer investigates and kills the buggy orchestrator

**Prevention**: Code review, chaos testing (spawn loops), and production telemetry (chain_depth histogram with alerts at 80% and 100% of max).

### 4. Secret Compromise

**Scenario**: The HMAC secret used to sign agent tokens is leaked. An attacker can forge arbitrary agent identities.

**Recovery**:
- Immediately rotate the HMAC secret via secure distribution to all agents/validators
- Invalidate all tokens signed with the old secret (set a cutoff timestamp)
- Force all agents to request fresh tokens from SPIRE or token service
- Broadcast a revocation for agent IDs issued in the compromise window

**Prevention**: Use SPIFFE/SPIRE (industry-standard minting) instead of HMAC where possible. Limit HMAC secret access to orchestrator and validator nodes. Enable audit logging of secret access.

## References

- [Trust & Byzantine Agents](trust-and-byzantine.md) — Agent output verification and fraud detection
- [Hierarchical Agent Networks](../patterns/integration/hierarchical-networks.md) — Network topology this pattern secures
- [chakraview-zero-trust-blueprint](https://github.com/gundu/chakraview-zero-trust-blueprint) — Original zero-trust reference architecture (services, not agents)
- **SPIFFE/SPIRE**: https://spiffe.io/ — Standard for workload identity and certificate management
- **RFC 8693**: OAuth 2.0 Token Exchange — Token delegation standard
