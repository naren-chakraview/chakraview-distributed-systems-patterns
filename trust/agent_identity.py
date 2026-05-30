"""
Agent Identity and Trust Tier structures.

Pattern: Zero Trust for Agents (see docs/foundations/zero-trust-for-agents.md)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class AgentTrustTier(Enum):
    """Agent trust tiers for progressive capability unlocking."""

    UNTRUSTED = "untrusted"
    LEAST_PRIVILEGE = "least_privilege"
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMIN = "admin"


@dataclass
class AgentPolicy:
    """Policy enforcement rules for an agent."""

    agent_name: str
    tier: AgentTrustTier
    allowed_actions: List[str] = field(default_factory=list)
    max_delegation_depth: int = 1
    can_delegate: bool = False
    requires_audit_log: bool = True
    can_access_sensitive_data: bool = False
    max_concurrent_operations: int = 10


@dataclass
class AgentIdentity:
    """Verifiable identity for an agent in a zero-trust system."""

    agent_id: str
    agent_name: str
    tier: AgentTrustTier
    policy: AgentPolicy
    signing_key: str  # Secret key for HMAC signing
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    active: bool = True

    def to_dict(self) -> Dict:
        """Convert identity to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "tier": self.tier.value,
            "policy": {
                "agent_name": self.policy.agent_name,
                "tier": self.policy.tier.value,
                "allowed_actions": self.policy.allowed_actions,
                "max_delegation_depth": self.policy.max_delegation_depth,
                "can_delegate": self.policy.can_delegate,
                "requires_audit_log": self.policy.requires_audit_log,
                "can_access_sensitive_data": self.policy.can_access_sensitive_data,
                "max_concurrent_operations": self.policy.max_concurrent_operations,
            },
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "active": self.active,
        }
