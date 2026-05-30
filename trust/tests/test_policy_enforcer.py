"""
16 unit tests for Zero Trust for Agents policy enforcement.

Pattern: Zero Trust for Agents (see docs/foundations/zero-trust-for-agents.md)
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from trust.agent_identity import AgentIdentity, AgentTrustTier, AgentPolicy
from trust.delegation_token import DelegationToken, ChainDepthExceededError
from trust.identity_registry import IdentityRegistry
from trust.policy_enforcer import PolicyEnforcer


@pytest.fixture
def registry():
    """Create and populate an identity registry."""
    reg = IdentityRegistry()
    policy_file = Path(__file__).parent.parent / "policies.yaml"
    reg.load_policies(str(policy_file))
    return reg


@pytest.fixture
def enforcer(registry):
    """Create a policy enforcer."""
    return PolicyEnforcer(registry)


class TestAgentIdentity:
    """Tests for AgentIdentity."""

    def test_agent_identity_creation(self):
        """Test creating an agent identity."""
        policy = AgentPolicy(
            agent_name="Test Agent",
            tier=AgentTrustTier.STANDARD,
            allowed_actions=["read", "write"],
        )
        identity = AgentIdentity(
            agent_id="agent-1",
            agent_name="Test Agent",
            tier=AgentTrustTier.STANDARD,
            policy=policy,
            signing_key="test-secret-12345",
        )
        assert identity.agent_id == "agent-1"
        assert identity.agent_name == "Test Agent"
        assert identity.tier == AgentTrustTier.STANDARD
        assert identity.active is True

    def test_agent_identity_to_dict(self):
        """Test converting agent identity to dictionary."""
        policy = AgentPolicy(
            agent_name="Test Agent",
            tier=AgentTrustTier.STANDARD,
            allowed_actions=["read"],
        )
        identity = AgentIdentity(
            agent_id="agent-1",
            agent_name="Test Agent",
            tier=AgentTrustTier.STANDARD,
            policy=policy,
            signing_key="test-secret-12345",
        )
        result = identity.to_dict()
        assert result["agent_id"] == "agent-1"
        assert result["agent_name"] == "Test Agent"
        assert result["tier"] == "standard"
        assert result["active"] is True


class TestDelegationToken:
    """Tests for DelegationToken."""

    def test_token_creation(self):
        """Test creating a delegation token."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
        )
        assert token.issuer_id == "agent-1"
        assert token.subject_id == "agent-2"
        assert token.action == "delegate"
        assert len(token.chain) == 1
        assert token.chain[0] == "agent-1"

    def test_token_signing_and_verification(self):
        """Test token HMAC signing and verification."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
        )
        secret = "test-secret-12345"

        # Sign the token
        signature = token.sign(secret)
        assert signature
        assert len(signature) == 64  # SHA256 hex = 64 chars

        # Verify the token
        assert token.verify(secret) is True

    def test_token_signature_fails_with_wrong_secret(self):
        """Test that signature verification fails with wrong secret."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
        )
        token.sign("test-secret-12345")

        # Verify with wrong secret fails
        assert token.verify("wrong-secret") is False

    def test_token_expiration(self):
        """Test token expiration check."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert token.is_expired() is True

    def test_token_not_expired(self):
        """Test token expiration check when not expired."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        assert token.is_expired() is False

    def test_token_add_delegation(self):
        """Test adding delegators to token chain."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
        )
        token.add_delegation("agent-3", max_depth=3)
        token.add_delegation("agent-4", max_depth=3)

        assert len(token.chain) == 3
        assert token.chain == ["agent-1", "agent-3", "agent-4"]

    def test_token_delegation_chain_exceeds_depth(self):
        """Test that adding to chain beyond max depth raises error."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
        )
        with pytest.raises(ChainDepthExceededError):
            token.add_delegation("agent-3", max_depth=1)

    def test_token_to_dict(self):
        """Test converting token to dictionary."""
        token = DelegationToken(
            issuer_id="agent-1",
            subject_id="agent-2",
            action="delegate",
        )
        token.sign("test-secret-12345")
        result = token.to_dict()

        assert result["issuer_id"] == "agent-1"
        assert result["subject_id"] == "agent-2"
        assert result["action"] == "delegate"
        assert len(result["signature"]) == 64


class TestPolicyEnforcer:
    """Tests for PolicyEnforcer."""

    def test_enforce_valid_request(self, enforcer, registry):
        """Test enforcement of a valid request."""
        agent = registry.get_agent("agent-orchestrator")
        token = DelegationToken(
            issuer_id="agent-orchestrator",
            subject_id="agent-orchestrator",
            action="orchestrate",
        )
        token.sign("test-secret-12345")

        allowed, reason = enforcer.enforce(
            "agent-orchestrator",
            token,
            "orchestrate",
        )
        assert allowed is True
        assert "passed" in reason.lower()

    def test_enforce_agent_not_found(self, enforcer):
        """Test enforcement when agent is not found."""
        token = DelegationToken(
            issuer_id="unknown",
            subject_id="unknown",
            action="read",
        )

        allowed, reason = enforcer.enforce("unknown", token, "read")
        assert allowed is False
        assert "not found" in reason.lower()

    def test_enforce_token_subject_mismatch(self, enforcer, registry):
        """Test enforcement fails when token subject doesn't match agent."""
        token = DelegationToken(
            issuer_id="agent-orchestrator",
            subject_id="agent-intent",  # Mismatch
            action="orchestrate",
        )
        token.sign("test-secret-12345")

        allowed, reason = enforcer.enforce(
            "agent-orchestrator",
            token,
            "orchestrate",
        )
        assert allowed is False
        assert "subject" in reason.lower()

    def test_enforce_token_expired(self, enforcer, registry):
        """Test enforcement fails when token is expired."""
        token = DelegationToken(
            issuer_id="agent-orchestrator",
            subject_id="agent-orchestrator",
            action="orchestrate",
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        token.sign("test-secret-12345")

        allowed, reason = enforcer.enforce(
            "agent-orchestrator",
            token,
            "orchestrate",
        )
        assert allowed is False
        assert "expired" in reason.lower()

    def test_enforce_invalid_signature(self, enforcer, registry):
        """Test enforcement fails with invalid signature."""
        token = DelegationToken(
            issuer_id="agent-orchestrator",
            subject_id="agent-orchestrator",
            action="orchestrate",
        )
        token.sign("test-secret-12345")
        token.signature = "invalid" + token.signature[7:]  # Corrupt signature

        allowed, reason = enforcer.enforce(
            "agent-orchestrator",
            token,
            "orchestrate",
        )
        assert allowed is False
        assert "signature" in reason.lower()

    def test_enforce_action_not_authorized(self, enforcer, registry):
        """Test enforcement fails when action not in allowed_actions."""
        token = DelegationToken(
            issuer_id="agent-segment",
            subject_id="agent-segment",
            action="read_profiles",  # Valid action
        )
        token.sign("test-secret-12345")

        allowed, reason = enforcer.enforce(
            "agent-segment",
            token,
            "write_profiles",  # Invalid action
        )
        assert allowed is False
        assert "not in allowed_actions" in reason.lower()

    def test_enforce_delegation_chain_exceeds_depth(self, enforcer, registry):
        """Test enforcement fails when delegation chain exceeds depth."""
        token = DelegationToken(
            issuer_id="agent-segment",
            subject_id="agent-segment",
            action="segment_customers",
        )
        # Add delegations beyond max_delegation_depth (1 for agent-segment)
        token.chain = ["agent-1", "agent-2", "agent-3"]  # Depth = 3

        token.sign("test-secret-12345")

        allowed, reason = enforcer.enforce(
            "agent-segment",
            token,
            "segment_customers",
        )
        assert allowed is False
        assert "chain depth" in reason.lower()

    def test_enforce_sensitive_data_access_denied(self, enforcer, registry):
        """Test enforcement fails for sensitive data without permission."""
        token = DelegationToken(
            issuer_id="agent-segment",
            subject_id="agent-segment",
            action="read_profiles",
        )
        token.sign("test-secret-12345")

        allowed, reason = enforcer.enforce(
            "agent-segment",
            token,
            "read_profiles",
            requires_sensitive_data=True,
        )
        assert allowed is False
        assert "sensitive data" in reason.lower()

    def test_enforce_sensitive_data_access_allowed(self, enforcer, registry):
        """Test enforcement allows sensitive data with permission."""
        token = DelegationToken(
            issuer_id="agent-fraud",
            subject_id="agent-fraud",
            action="access_payment_data",
        )
        token.sign("test-secret-12345")

        allowed, reason = enforcer.enforce(
            "agent-fraud",
            token,
            "access_payment_data",
            requires_sensitive_data=True,
        )
        assert allowed is True

    def test_enforce_rate_limit_exceeded(self, enforcer, registry):
        """Test enforcement fails when rate limit exceeded."""
        token = DelegationToken(
            issuer_id="agent-trends",
            subject_id="agent-trends",
            action="analyze_trends",
        )
        token.sign("test-secret-12345")

        # Set operation count to max
        enforcer._operation_counts["agent-trends"] = 3

        allowed, reason = enforcer.enforce(
            "agent-trends",
            token,
            "analyze_trends",
        )
        assert allowed is False
        assert "concurrent operations" in reason.lower()

    def test_enforce_rate_limit_within_limit(self, enforcer, registry):
        """Test enforcement succeeds when within rate limit."""
        token = DelegationToken(
            issuer_id="agent-trends",
            subject_id="agent-trends",
            action="analyze_trends",
        )
        token.sign("test-secret-12345")

        # Reset operation count
        enforcer._operation_counts["agent-trends"] = 0

        allowed, reason = enforcer.enforce(
            "agent-trends",
            token,
            "analyze_trends",
        )
        assert allowed is True

    def test_operation_count_tracking(self, enforcer):
        """Test operation count tracking."""
        agent_id = "agent-test"

        assert enforcer.get_operation_count(agent_id) == 0

        enforcer.record_operation_start(agent_id)
        assert enforcer.get_operation_count(agent_id) == 1

        enforcer.record_operation_start(agent_id)
        assert enforcer.get_operation_count(agent_id) == 2

        enforcer.record_operation_end(agent_id)
        assert enforcer.get_operation_count(agent_id) == 1

        enforcer.record_operation_end(agent_id)
        assert enforcer.get_operation_count(agent_id) == 0

    def test_identity_registry_loads_policies(self, registry):
        """Test that identity registry loads policies from YAML."""
        agents = registry.list_agents()

        assert len(agents) == 5
        assert "agent-orchestrator" in agents
        assert "agent-intent" in agents
        assert "agent-fraud" in agents
        assert "agent-segment" in agents
        assert "agent-trends" in agents

        orchestrator = agents["agent-orchestrator"]
        assert orchestrator.tier == AgentTrustTier.ELEVATED
        assert orchestrator.policy.can_delegate is True
        assert orchestrator.policy.can_access_sensitive_data is True
