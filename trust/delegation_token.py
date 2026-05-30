"""
Delegation Token with On-Behalf-Of (OBO) chain and HMAC-SHA256 signing.

Pattern: Zero Trust for Agents (see docs/foundations/zero-trust-for-agents.md)
"""

import hmac
import hashlib
import json
import base64
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta


class ChainDepthExceededError(Exception):
    """Raised when delegation chain depth exceeds policy limit."""

    pass


@dataclass
class DelegationToken:
    """
    A token representing delegated authority with On-Behalf-Of chain.

    Includes cryptographic proof of delegation and chain-of-custody.
    """

    issuer_id: str  # Agent issuing the token
    subject_id: str  # Agent receiving delegation
    action: str  # Action being delegated
    chain: List[str] = field(default_factory=list)  # OBO chain: [issuer, delegator1, delegator2, ...]
    issued_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    signature: str = ""  # HMAC-SHA256 signature

    def __post_init__(self):
        """Initialize chain if empty."""
        if not self.chain:
            self.chain = [self.issuer_id]
        if self.expires_at is None:
            self.expires_at = datetime.utcnow() + timedelta(hours=1)

    def add_delegation(self, delegator_id: str, max_depth: int) -> None:
        """
        Add a delegator to the chain.

        Args:
            delegator_id: ID of the agent adding themselves to the chain
            max_depth: Maximum allowed chain depth from policy

        Raises:
            ChainDepthExceededError: If chain depth would exceed max_depth
        """
        if len(self.chain) >= max_depth:
            raise ChainDepthExceededError(
                f"Delegation chain depth {len(self.chain)} would exceed max {max_depth}"
            )
        self.chain.append(delegator_id)

    def sign(self, secret: str) -> str:
        """
        Create HMAC-SHA256 signature over token payload.

        Args:
            secret: Secret key for signing

        Returns:
            Hex-encoded signature
        """
        payload = {
            "issuer_id": self.issuer_id,
            "subject_id": self.subject_id,
            "action": self.action,
            "chain": self.chain,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(), payload_json.encode(), hashlib.sha256
        ).hexdigest()
        self.signature = signature
        return signature

    def verify(self, secret: str) -> bool:
        """
        Verify token signature using HMAC-SHA256.

        Args:
            secret: Secret key for verification

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.signature:
            return False

        # Compute expected signature without modifying self.signature
        payload = {
            "issuer_id": self.issuer_id,
            "subject_id": self.subject_id,
            "action": self.action,
            "chain": self.chain,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
        payload_json = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(), payload_json.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(self.signature, expected_signature)

    def is_expired(self) -> bool:
        """Check if token has expired."""
        return self.expires_at is not None and datetime.utcnow() > self.expires_at

    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        return {
            "issuer_id": self.issuer_id,
            "subject_id": self.subject_id,
            "action": self.action,
            "chain": self.chain,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "signature": self.signature,
        }

    def to_json(self) -> str:
        """Convert token to JSON string."""
        return json.dumps(self.to_dict())
