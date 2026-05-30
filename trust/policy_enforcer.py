"""
Policy Enforcer with 6-check zero-trust pipeline.

Pattern: Zero Trust for Agents (see docs/foundations/zero-trust-for-agents.md)
"""

from typing import Optional, Tuple
from datetime import datetime

from trust.agent_identity import AgentIdentity, AgentTrustTier
from trust.delegation_token import DelegationToken
from trust.identity_registry import IdentityRegistry


class PolicyEnforcer:
    """
    Enforces zero-trust policies through a 6-check pipeline.

    Checks:
    1. Agent identity verification (agent exists and is active)
    2. Token validity (signature, expiration, subject match)
    3. Action authorization (action in allowed_actions)
    4. Delegation chain validation (depth <= max_delegation_depth)
    5. Sensitive data access control (can_access_sensitive_data)
    6. Rate limiting (concurrent operations < max_concurrent_operations)
    """

    def __init__(self, registry: IdentityRegistry):
        """
        Initialize enforcer with an identity registry.

        Args:
            registry: IdentityRegistry for agent lookups
        """
        self.registry = registry
        self._operation_counts = {}  # Track concurrent operations per agent

    def enforce(
        self,
        agent_id: str,
        token: DelegationToken,
        action: str,
        requires_sensitive_data: bool = False,
    ) -> Tuple[bool, str]:
        """
        Enforce zero-trust policy through 6-check pipeline.

        Args:
            agent_id: ID of the agent requesting access
            token: DelegationToken authorizing the action
            action: Action being requested
            requires_sensitive_data: Whether the action requires sensitive data access

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Check 1: Agent identity verification
        allowed, reason = self._check_agent_identity(agent_id)
        if not allowed:
            return False, reason

        agent = self.registry.get_agent(agent_id)

        # Check 2: Token validity
        allowed, reason = self._check_token_validity(token, agent_id)
        if not allowed:
            return False, reason

        # Check 3: Action authorization
        allowed, reason = self._check_action_authorization(agent, action)
        if not allowed:
            return False, reason

        # Check 4: Delegation chain validation
        allowed, reason = self._check_delegation_chain(token, agent.policy.max_delegation_depth)
        if not allowed:
            return False, reason

        # Check 5: Sensitive data access control
        if requires_sensitive_data:
            allowed, reason = self._check_sensitive_data_access(agent)
            if not allowed:
                return False, reason

        # Check 6: Rate limiting
        allowed, reason = self._check_rate_limit(agent_id, agent.policy.max_concurrent_operations)
        if not allowed:
            return False, reason

        return True, "All checks passed"

    def _check_agent_identity(self, agent_id: str) -> Tuple[bool, str]:
        """
        Check 1: Verify agent exists and is active.

        Args:
            agent_id: Agent ID to verify

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        if not self.registry.verify_agent_active(agent_id):
            return False, f"Agent {agent_id} not found or not active"
        return True, "Agent identity verified"

    def _check_token_validity(self, token: DelegationToken, subject_id: str) -> Tuple[bool, str]:
        """
        Check 2: Verify token signature, expiration, and subject match.

        Args:
            token: Token to verify
            subject_id: Expected subject ID

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Check subject match
        if token.subject_id != subject_id:
            return False, f"Token subject {token.subject_id} does not match agent {subject_id}"

        # Check expiration
        if token.is_expired():
            return False, "Token has expired"

        # Check signature (use the subject agent's signing key)
        subject_agent = self.registry.get_agent(subject_id)
        if not subject_agent:
            return False, "Subject agent not found for signature verification"

        if not token.verify(subject_agent.signing_key):
            return False, "Token signature verification failed"

        return True, "Token is valid"

    def _check_action_authorization(self, agent: AgentIdentity, action: str) -> Tuple[bool, str]:
        """
        Check 3: Verify action is in agent's allowed_actions.

        Args:
            agent: Agent identity
            action: Action being requested

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        if action not in agent.policy.allowed_actions:
            return (
                False,
                f"Action {action} not in allowed_actions for {agent.agent_name}",
            )
        return True, f"Action {action} is authorized"

    def _check_delegation_chain(self, token: DelegationToken, max_depth: int) -> Tuple[bool, str]:
        """
        Check 4: Verify delegation chain depth does not exceed policy maximum.

        Args:
            token: Token with delegation chain
            max_depth: Maximum allowed chain depth

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        chain_length = len(token.chain)
        if chain_length > max_depth:
            return (
                False,
                f"Delegation chain depth {chain_length} exceeds max {max_depth}",
            )
        return True, f"Chain depth {chain_length} within limit {max_depth}"

    def _check_sensitive_data_access(self, agent: AgentIdentity) -> Tuple[bool, str]:
        """
        Check 5: Verify agent has permission to access sensitive data.

        Args:
            agent: Agent identity

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        if not agent.policy.can_access_sensitive_data:
            return False, f"Agent {agent.agent_name} does not have sensitive data access"
        return True, "Agent has sensitive data access permission"

    def _check_rate_limit(self, agent_id: str, max_concurrent: int) -> Tuple[bool, str]:
        """
        Check 6: Verify agent has not exceeded concurrent operation limit.

        Args:
            agent_id: Agent ID
            max_concurrent: Maximum concurrent operations allowed

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        current_count = self._operation_counts.get(agent_id, 0)
        if current_count >= max_concurrent:
            return (
                False,
                f"Agent {agent_id} has {current_count} concurrent operations (max {max_concurrent})",
            )

        # Increment operation count
        self._operation_counts[agent_id] = current_count + 1
        return True, f"Operation within limit ({current_count + 1}/{max_concurrent})"

    def record_operation_start(self, agent_id: str) -> None:
        """
        Record the start of an operation for an agent.

        Args:
            agent_id: Agent ID
        """
        current = self._operation_counts.get(agent_id, 0)
        self._operation_counts[agent_id] = current + 1

    def record_operation_end(self, agent_id: str) -> None:
        """
        Record the end of an operation for an agent.

        Args:
            agent_id: Agent ID
        """
        current = self._operation_counts.get(agent_id, 0)
        if current > 0:
            self._operation_counts[agent_id] = current - 1
        else:
            self._operation_counts[agent_id] = 0

    def reset_operation_counts(self) -> None:
        """Reset all operation counts."""
        self._operation_counts = {}

    def get_operation_count(self, agent_id: str) -> int:
        """
        Get current operation count for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Current operation count
        """
        return self._operation_counts.get(agent_id, 0)
