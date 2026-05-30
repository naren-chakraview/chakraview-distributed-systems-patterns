# Pattern Cross-References

This file maintains links from pattern documentation to reference implementation code.

## Zero Trust for Agents

**Documentation:** `docs/foundations/zero-trust-for-agents.md`

**Code Examples:**
- Agent identity types: `trust/agent_identity.py:1-60`
- Delegation token with OBO: `trust/delegation_token.py:1-150`
- Policy enforcer: `trust/policy_enforcer.py:1-100`
- Identity registry: `trust/identity_registry.py:1-80`
- Unit tests: `trust/tests/test_policy_enforcer.py`
- Policy definitions: `trust/policies.yaml`
- Proto definition: `shared/proto/messages.proto:AgentIdentity message`

**Related Patterns:**
- Trust & Byzantine Agents: covers agent OUTPUT verification; this covers agent IDENTITY
- Hierarchical Agent Networks: deployment topology this pattern secures
