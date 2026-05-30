"""
Identity Registry with YAML-based policy loading.

Pattern: Zero Trust for Agents (see docs/foundations/zero-trust-for-agents.md)
"""

from typing import Dict, Optional
import yaml
from pathlib import Path

from trust.agent_identity import AgentIdentity, AgentTrustTier, AgentPolicy


class IdentityRegistry:
    """Registry for agent identities with policy enforcement."""

    def __init__(self):
        """Initialize empty registry."""
        self._agents: Dict[str, AgentIdentity] = {}

    def register_agent(self, identity: AgentIdentity) -> None:
        """
        Register an agent identity.

        Args:
            identity: AgentIdentity to register
        """
        self._agents[identity.agent_id] = identity

    def get_agent(self, agent_id: str) -> Optional[AgentIdentity]:
        """
        Retrieve agent identity by ID.

        Args:
            agent_id: Agent ID to look up

        Returns:
            AgentIdentity if found, None otherwise
        """
        return self._agents.get(agent_id)

    def list_agents(self) -> Dict[str, AgentIdentity]:
        """
        List all registered agents.

        Returns:
            Dictionary mapping agent IDs to identities
        """
        return dict(self._agents)

    def load_policies(self, policy_file: str) -> None:
        """
        Load agent policies from YAML file.

        Args:
            policy_file: Path to YAML policy file
        """
        with open(policy_file, "r") as f:
            policies = yaml.safe_load(f)

        if not policies or "agents" not in policies:
            return

        for agent_config in policies["agents"]:
            agent_name = agent_config["name"]
            tier = AgentTrustTier(agent_config["tier"])
            signing_key = agent_config.get("signing_key", "test-secret-12345")

            policy = AgentPolicy(
                agent_name=agent_name,
                tier=tier,
                allowed_actions=agent_config.get("allowed_actions", []),
                max_delegation_depth=agent_config.get("max_delegation_depth", 1),
                can_delegate=agent_config.get("can_delegate", False),
                requires_audit_log=agent_config.get("requires_audit_log", True),
                can_access_sensitive_data=agent_config.get("can_access_sensitive_data", False),
                max_concurrent_operations=agent_config.get("max_concurrent_operations", 10),
            )

            identity = AgentIdentity(
                agent_id=agent_config["id"],
                agent_name=agent_name,
                tier=tier,
                policy=policy,
                signing_key=signing_key,
            )

            self.register_agent(identity)

    def verify_agent_active(self, agent_id: str) -> bool:
        """
        Verify that an agent is active.

        Args:
            agent_id: Agent ID to verify

        Returns:
            True if agent is active, False otherwise
        """
        agent = self.get_agent(agent_id)
        return agent is not None and agent.active

    def deactivate_agent(self, agent_id: str) -> bool:
        """
        Deactivate an agent.

        Args:
            agent_id: Agent ID to deactivate

        Returns:
            True if agent was deactivated, False if not found
        """
        agent = self.get_agent(agent_id)
        if agent:
            agent.active = False
            return True
        return False
