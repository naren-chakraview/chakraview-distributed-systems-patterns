# ADR-0002: Zero Trust Agent Identities

**Date:** 2026-05-29  
**Status:** Accepted

## Problem

Agent systems introduce a third class of identity—distinct from human (IAM) and service (SPIFFE) identities—with unique characteristics:

- **Dynamic spawning**: Agents are created at runtime in response to orchestration decisions or user requests
- **Ephemeral lifespans**: TTLs range from seconds (edge) to minutes (cloud), compared to hours or days for service identities
- **Capability variance**: Each agent instantiation has a specific set of permitted actions; agents cannot escalate privileges beyond their class
- **Delegation chains**: Agents may spawn sub-agents, forming multi-hop authorization chains
- **Heterogeneous trust tiers**: Agents run on orchestrators (trusted), cloud infrastructure (semi-trusted), and edge devices (least-trusted)
- **No pre-registration**: Unlike services, agents cannot be registered in advance; identity must be established at spawn time

Existing zero-trust frameworks (chakraview-zero-trust-blueprint, SPIFFE/SPIRE) assume stable, pre-registered identities and a single trust vector. They do not address:

1. **Verification of agent identity across delegation chains** — How does a cloud service verify that a request from an edge agent is legitimate and within its parent's delegation scope?
2. **Capability enforcement** — How do we prevent an edge agent from calling APIs reserved for cloud agents?
3. **Rapid revocation and expiry** — How do we revoke or expire identities in sub-minute timeframes without constant synchronization?

This ADR establishes the three-plane (identity, tier authorization, capability policy) architecture for agent authorization.

## Decision

Implement a **three-plane zero-trust model for agents**, adapted from zero-trust principles but specialized for ephemeral identities:

### Plane 1: Identity (AgentIdentity Token)

Each agent receives a cryptographically signed identity token at spawn time:

```protobuf
message AgentIdentity {
  string agent_id = 1;
  string agent_type = 2;            // "orchestrator", "cloud_agent", "edge_agent"
  string trust_tier = 3;             // Hierarchical: orchestrator > cloud > edge
  repeated string capabilities = 4;  // Granted permissions: ["spawn_sub_agent", "log_metric", ...]
  string issuer = 5;                 // Identity of spawning orchestrator/agent
  int64 issued_at = 6;               // Unix timestamp
  int64 expires_at = 7;              // TTL: 30s (edge), 120s (cloud), 300s (orch)
  string parent_agent_id = 8;        // Null if spawned by system; otherwise parent's ID
}
```

**Token format**: SPIFFE JWT SVIDs (production) or HMAC-signed JSON (edge/offline).

**TTLs by tier**:
- Edge agents: 30 seconds (accommodate device churn and reconnection)
- Cloud agents: 120 seconds (support longer-running operations)
- Orchestrators: 300 seconds (reduce spawning overhead)

### Plane 2: Tier Authorization (Hierarchy)

A three-tier trust hierarchy:

```
Tier 0 (Orchestrator)    ← can spawn cloud and edge agents
Tier 1 (Cloud Agent)     ← can spawn edge agents only
Tier 2 (Edge Agent)      ← cannot spawn further
```

Every call target (API endpoint, spawn, delegation) specifies `allowed_caller_tiers`. The caller must belong to an allowed tier, forming a deny-by-default authorization model.

### Plane 3: Capability Policy (Grant-Based)

Each agent type has a static set of allowed capabilities. A call succeeds if `request.capabilities ⊆ agent.capabilities`.

Example:
```yaml
agent_types:
  edge_agent:
    allowed_capabilities: [log_metric, sync_state, query_local_cache]
  cloud_agent:
    allowed_capabilities: [log_metric, query_api, spawn_sub_agent, sync_state]
  orchestrator:
    allowed_capabilities: [spawn_sub_agent, escalate_alert, revoke_agent, publish_policy]
```

### Chain Depth Enforcement

To prevent runaway delegation, each request includes a `caller_chain` (list of agent IDs that led to the current call). If `chain_depth >= max_delegation_depth` (default: 5), the request is denied.

## Consequences

### Operational Burden

1. **SPIRE deployment** (if using SPIFFE): Requires running a SPIRE agent on all deployment targets (orchestrators, cloud compute, edge devices).
2. **Token service**: For offline edge scenarios, a pre-deployment step seeds agents with HMAC-signed tokens; rotation requires manual distribution or a secure update mechanism.
3. **Policy management**: Agent type policies must be defined in YAML and hot-reloaded or baked into container images.
4. **Secret rotation**: HMAC secrets must be rotated periodically; all validators must be updated in a coordinated window.

### Security Gains

1. **Least-privilege enforcement**: Each agent operates with only the capabilities it needs; a compromised agent cannot escalate.
2. **Delegation control**: Sub-agents cannot exceed their parent's permissions; depth limits prevent runaway spawning.
3. **Audit trail**: Every authorization decision is logged with full context (caller, target, decision, chain depth), enabling forensic analysis.
4. **Rapid revocation**: Sub-minute TTLs and revocation lists allow quick lockdown in case of breach.

### Auditability

All authorization decisions are logged as JSON events:

```json
{
  "timestamp": "2026-05-29T10:30:45.123Z",
  "enforcement_id": "enf-abc123",
  "caller": { "agent_id": "...", "trust_tier": "cloud_agent" },
  "action": "spawn_sub_agent",
  "decision": "ALLOW",
  "chain_depth": 2,
  "ttl_remaining_seconds": 87,
  "validation_latency_ms": 2.3
}
```

This enables compliance reporting (e.g., "all sub-agent spawns in the last hour") and incident investigation.

### Latency Impact

Token validation (HMAC check or SPIFFE SVID validation) adds **1–5ms** per call. For most agentic workloads (latency budgets in 100s of ms), this is acceptable. Real-time control systems (millisecond-scale) may need caching or pre-computed delegations.

### Chain Depth Constraint

The `max_delegation_depth` limit (default: 5) prevents unbounded recursion but also limits legitimate use cases where agents legitimately delegate many hops. This is a tunable trade-off; deeper chains can be allowed with caution and additional monitoring.

## References

- [Zero Trust for Agents](../foundations/zero-trust-for-agents.md) — Full pattern specification
- [Hierarchical Agent Networks](../patterns/integration/hierarchical-networks.md) — Network topology secured by this pattern
- SPIFFE/SPIRE: https://spiffe.io/
- RFC 8693: OAuth 2.0 Token Exchange
