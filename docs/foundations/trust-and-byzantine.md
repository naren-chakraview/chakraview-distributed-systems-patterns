# Trust & Byzantine Agents

## Problem Statement

In edge+cloud systems, agents may be deployed on untrusted edge devices, or coordinating with external agents. Can we trust an agent to report state accurately? What if an agent lies about its results, or claims it succeeded when it failed?

Byzantine Fault Tolerance (BFT) addresses this: how to reach consensus even when some participants are untrusted.

## Solution Approach

**Trust Models:**

1. **Trusted agents** — deployed on trusted infrastructure; assume honest behavior
2. **Untrusted agents** — deployed on edge/external; may lie or malfunction
3. **Partially trusted** — most agents honest; bounded fraction may be faulty

**Verification Strategies:**

- **Cryptographic commitment** — agent signs decision before revealing details; can't later claim it was different
- **Voting/quorum** — require majority agreement before accepting result (BFT: tolerate up to f faulty agents with 3f+1 total)
- **Audit trails** — log all decisions with proofs (execution traces, output hashes)
- **Spot checks** — randomly re-execute agent decision; validate against logged result

**For Agents Specifically:**

- Sign model outputs (if model supports); proves which model generated output
- Hash conversation history at key points; detects tampering
- Use quorum for critical decisions (e.g., payment authorization; require 2-of-3 agents agree)
- Separate authority: edge agent can't approve its own decisions; cloud agent must verify

## When to Use

**Trusted agents (no BFT):**
- Agents on corporate infrastructure
- Agents with code provenance/audit
- Non-critical decisions (e.g., summarization, recommendations)

**Untrusted agents (BFT required):**
- Agents on user devices or external partners
- Critical decisions (financial, security, privacy)
- Multi-party workflows (no single party should control outcome)

## Trade-offs

| Approach | Security | Overhead | Latency |
|----------|----------|----------|---------|
| **Trusted agents** | Low (trust-based) | None | Low |
| **Cryptographic commitment** | High (unforgeable proof) | Signing/verification cost | Low |
| **Voting (f faulty, 3f+1 agents)** | High (byzantine fault tolerant) | 3x replication + coordination | High (wait for consensus) |
| **Spot checks** | Medium (probabilistic) | Sampling cost | Low (async verification) |

**Recommendation:** For edge+cloud, use trusted agents within cloud tier; use cryptographic commitment + spot checks for edge agents; use voting only for mission-critical decisions.

## Observability Hooks

**Metrics:**
- Consensus reach time (voting latency)
- Agent agreement rate (% decisions where all agents agree)
- Spot check failure rate (% when replay differs from logged result)
- Signature verification failures

**Queries:**
- "Has any agent deviated from majority decision?"
- "Which agents have unverified outputs?"
- "When did spot check fail?"

## Example: Quorum for Payment Authorization

**Scenario:** Three-agent quorum decides whether to authorize payment > $10K.

- Edge agent A evaluates payment request
- Cloud agent B evaluates fraud signals
- Cloud agent C evaluates account limits
- Quorum: require 2-of-3 approval; each agent signs decision
- If A claims approval but only B+C approved: reject (A lying or miscommunicating)
- If A+B approved but C says deny: reject (quorum failed; require recount)

**Benefit:** Single faulty agent can't authorize fraudulent payment.

## References

- [Consistency Models](consistency-models.md)
- [Agent Placement](../patterns/edge-cloud-deployment/agent-placement.md)
- Castro, M., Liskov, B. (2002). "Practical Byzantine Fault Tolerance"
