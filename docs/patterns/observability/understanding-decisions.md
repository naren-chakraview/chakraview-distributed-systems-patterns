# Understanding Model Decisions

## Problem Statement

Agent outputs are opaque. User asks a question; agent gives an answer. But *why*? Which input tokens influenced the answer? Did the agent consider the context, or hallucinate? What if the answer is wrong — can we trace what went wrong?

Understanding model decisions is critical for debugging, auditing, and trust.

## Solution Approach

**Techniques:**

1. **Token attribution** — identify which input tokens contributed to each output token
2. **Attention visualization** — if model exposes attention, visualize which parts of input are weighted
3. **Decision tree reconstruction** — break agent decision into steps; log reasoning at each step
4. **Confidence scores** — if model provides logprobs or confidence, surface them
5. **Prompt analysis** — what system prompt was used? Did it influence the decision?
6. **Embedding analysis** — compare embeddings of user input + context + output; detect outliers

**Token Attribution (Simple Approach):**

- Run inference twice: once normal, once with permuted input
- Compare outputs; which permutations changed the output? Those tokens contributed
- Expensive but accurate (O(n) evaluations)

**Structured Reasoning:**

- Ask agent to explain decisions: "Break down your reasoning into steps"
- Log each step; parse for logic
- Validate steps align with context

**Confidence Signals:**

- If LLM exposes top-k alternatives, log them: decision + alternatives indicate uncertainty
- Use temperature/sampling: if sampling multiple times produces vastly different answers, decision is uncertain

## When to Use

- Use for **auditable decisions** (financial, security, privacy impact)
- Use for **debugging** (agent gave wrong answer; trace why)
- Use for **learning** (collect decision explanations; improve prompts)
- Skip for **low-stakes** (summarization, suggestions where error tolerance is high)

## Trade-offs

| Technique | Interpretability | Overhead | Latency |
|-----------|-----------------|----------|---------|
| **Structured reasoning** | High (explicit steps) | Medium (extra LLM inference) | High (2-3x slower) |
| **Token attribution** | Very high (precise) | Very high (O(n) evaluations) | Very high (n× slower) |
| **Confidence scores** | Medium (indicates uncertainty) | None (native to model) | None |
| **Prompt inspection** | Medium (explains system behavior) | None (log existing prompt) | None |
| **Embedding comparison** | Low (abstract space) | Low (cosine similarity) | None |

**Recommendation:** Always log confidence scores; use structured reasoning for critical decisions; use token attribution for debugging specific issues.

## Example: Debugging Wrong Decision

**Scenario:** Agent approves $100K expense; should have rejected.

**Tracing:**
1. Log confidence score: model reported 62% confidence (below 80% threshold) — why wasn't it caught?
2. Log system prompt: was it trained to be lenient? ✓ Yes, "approved by default unless obvious fraud"
3. Structured reasoning: "I approved because: (1) amount is in range, (2) approval authority exists, (3) no fraud signals"
4. Token attribution: which input tokens influenced "approve"? Trace back → "Bob is VP of Finance" token weighted heavily
5. Hypothesis: agent trusted that VP can approve without checking actual authority limits

**Recovery:** Reduce prompt leniency; add explicit authority checks; alert on low-confidence approvals.

## Observability Hooks

**Metrics:**
- Decision confidence distribution (p50, p99 confidence)
- Structured reasoning quality (% of steps validated)
- Confidence mismatches (cases where high confidence = wrong answer)

**Queries:**
- "Show all decisions with confidence < X%"
- "What input tokens influenced this decision?"
- "Which system prompts led to wrong decisions?"
- "Which agents have low confidence on easy tasks?" (potential bug)

## References

- [Distributed Tracing](distributed-tracing.md)
- [Agent Health Metrics](agent-health-metrics.md)
- Ribeiro, M. T., et al. (2016). "'Why Should I Trust You?': Explaining the Predictions of Any Classifier"
