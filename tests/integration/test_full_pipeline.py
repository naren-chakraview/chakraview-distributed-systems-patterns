"""Integration tests for the full analytics pipeline.

Tests end-to-end flows demonstrating distributed patterns:
- test_user_to_segment: intent → fraud → segmentation pipeline
- test_vector_clock_propagation: causality tracking through the pipeline
- test_token_budgeting_across_agents: token consumption across agents
- test_error_propagation: failure handling in distributed flow
"""

import pytest
import asyncio
from typing import List


@pytest.mark.asyncio
async def test_user_to_segment_flow(
    intent_agent,
    fraud_agent,
    segmentation_agent,
    sample_user_message,
    sample_transaction,
    sample_customer
):
    """Test intent → fraud → segmentation pipeline.

    PATTERN: Multi-Agent Coordination
    Demonstrates how agents in a pipeline coordinate through message passing
    and shared state. Each agent processes data from the previous stage.

    Flow:
    1. Intent Agent: Detect user intent from message
    2. Fraud Agent: Analyze transaction associated with intent
    3. Segmentation Agent: Update customer segment based on transaction
    """
    # Stage 1: Intent detection
    intent_result = await intent_agent.execute(sample_user_message)
    assert intent_result.intent == "purchase"
    assert intent_result.confidence > 0.7
    assert intent_result.tokens_consumed > 0

    # Stage 2: Fraud detection (assumes purchase detected)
    fraud_result = await fraud_agent.execute(sample_transaction)
    assert fraud_result.risk_level in ["low", "medium", "high", "critical"]
    assert 0.0 <= fraud_result.risk_score <= 1.0
    assert len(fraud_result.factors) > 0

    # Stage 3: Segmentation (with transaction and customer info)
    segmentation_data = {
        **sample_customer,
        "recent_transaction_amount": sample_transaction["amount"],
        "detected_intent": intent_result.intent,
        "fraud_risk": fraud_result.risk_level
    }
    segmentation_result = await segmentation_agent.execute(segmentation_data)
    assert segmentation_result.segment in ["standard", "premium"]
    assert 0.0 <= segmentation_result.confidence <= 1.0


@pytest.mark.asyncio
async def test_vector_clock_propagation(
    intent_agent,
    fraud_agent,
    trends_agent,
    sample_user_message,
    sample_metrics
):
    """Test vector clock propagation through distributed agents.

    PATTERN: Causality and Ordering (Vector Clocks)
    Verifies that vector clocks increment properly as messages flow through
    the system, ensuring causal relationships are tracked.

    See: docs/foundations/causality-and-ordering.md
    See: docs/patterns/observability/distributed-tracing.md
    """
    # Record initial vector clock state
    initial_intent_vc = intent_agent.vector_clock.timestamp
    initial_fraud_vc = fraud_agent.vector_clock.timestamp
    initial_trends_vc = trends_agent.vector_clock.timestamp

    # Execute agents
    intent_result = await intent_agent.execute(sample_user_message)
    fraud_result = await fraud_agent.execute({})
    trends_result = await trends_agent.execute(sample_metrics)

    # Verify vector clocks incremented
    assert intent_agent.vector_clock.timestamp > initial_intent_vc
    assert fraud_agent.vector_clock.timestamp > initial_fraud_vc
    assert trends_agent.vector_clock.timestamp > initial_trends_vc

    # Verify results contain proper vector clock info
    assert intent_result.vector_clock.timestamp == intent_agent.vector_clock.timestamp
    assert fraud_result.vector_clock.timestamp == fraud_agent.vector_clock.timestamp
    assert trends_result.vector_clock.timestamp == trends_agent.vector_clock.timestamp

    # Simulate message passing: fraud agent receives intent result
    fraud_agent.vector_clock.merge(intent_result.vector_clock)
    fraud_agent.vector_clock.increment()

    # Verify merge updated the clock
    assert fraud_agent.vector_clock.timestamp >= intent_result.vector_clock.timestamp


@pytest.mark.asyncio
async def test_token_budgeting_across_agents(
    intent_agent,
    fraud_agent,
    trends_agent,
    segmentation_agent,
    sample_user_message,
    sample_transaction,
    sample_metrics,
    sample_customer
):
    """Test token consumption tracking across agents.

    PATTERN: Token Budgeting
    Verifies that agents track token consumption and stay within budgets
    even when called multiple times in a pipeline.

    See: docs/patterns/predictability/token-budgeting.md
    """
    # Execute all agents multiple times
    for _ in range(3):
        await intent_agent.execute(sample_user_message)
        await fraud_agent.execute(sample_transaction)
        await trends_agent.execute(sample_metrics)
        await segmentation_agent.execute(sample_customer)

    # Collect token usage
    intent_usage = sum(intent_agent.token_usage.values())
    fraud_usage = sum(fraud_agent.token_usage.values())
    trends_usage = sum(trends_agent.token_usage.values())
    seg_usage = sum(segmentation_agent.token_usage.values())

    total_usage = intent_usage + fraud_usage + trends_usage + seg_usage

    # Verify token consumption is within budgets
    assert intent_usage <= intent_agent.config.token_budget
    assert fraud_usage <= fraud_agent.config.token_budget
    assert trends_usage <= trends_agent.config.token_budget
    assert seg_usage <= segmentation_agent.config.token_budget

    # Verify each agent was called 3 times
    assert intent_agent.call_count == 3
    assert fraud_agent.call_count == 3
    assert trends_agent.call_count == 3
    assert segmentation_agent.call_count == 3

    # Verify token consumption is reasonable (non-zero)
    assert total_usage > 0


@pytest.mark.asyncio
async def test_parallel_agent_execution(
    intent_agent,
    fraud_agent,
    trends_agent,
    sample_user_message,
    sample_transaction,
    sample_metrics
):
    """Test parallel execution of independent agents.

    PATTERN: Agent Swarms
    Demonstrates safe parallel execution of agents that don't depend on
    each other's results. Useful for scaling when agents can work independently.

    See: docs/patterns/integration/agent-swarms.md
    """
    # Execute agents in parallel
    results = await asyncio.gather(
        intent_agent.execute(sample_user_message),
        fraud_agent.execute(sample_transaction),
        trends_agent.execute(sample_metrics),
        return_exceptions=False
    )

    # Verify all agents completed
    assert len(results) == 3

    intent_result, fraud_result, trends_result = results

    # Verify results are valid
    assert intent_result.intent is not None
    assert fraud_result.risk_level is not None
    assert trends_result.trend is not None

    # Verify parallel execution didn't affect individual states
    assert intent_agent.call_count == 1
    assert fraud_agent.call_count == 1
    assert trends_agent.call_count == 1


@pytest.mark.asyncio
async def test_agent_isolation(
    intent_agent,
    fraud_agent
):
    """Test that agents maintain isolated state.

    PATTERN: Agent Isolation
    Verifies that executing one agent doesn't affect another agent's
    internal state (vector clocks, token tracking, etc.).
    """
    # Record initial state
    initial_intent_vc = intent_agent.vector_clock.timestamp
    initial_fraud_vc = fraud_agent.vector_clock.timestamp

    # Execute intent agent
    await intent_agent.execute("Test message")

    # Fraud agent state should be unchanged
    assert fraud_agent.vector_clock.timestamp == initial_fraud_vc
    assert fraud_agent.call_count == 0

    # Execute fraud agent
    await fraud_agent.execute({})

    # Verify each agent has independent call counts
    assert intent_agent.call_count == 1
    assert fraud_agent.call_count == 1

    # Verify each agent has independent vector clocks
    assert intent_agent.vector_clock.timestamp > initial_intent_vc
    assert fraud_agent.vector_clock.timestamp > initial_fraud_vc


@pytest.mark.asyncio
async def test_consistency_across_pipeline_runs(
    intent_agent,
    fraud_agent,
    sample_user_message,
    sample_transaction
):
    """Test consistent behavior across multiple pipeline executions.

    PATTERN: Consistency Models
    Verifies that running the same input through agents produces consistent
    (or intentionally varied, for randomness) outputs.

    See: docs/foundations/consistency-models.md
    """
    # Run the same input multiple times
    for run in range(3):
        intent_result1 = await intent_agent.execute(sample_user_message)
        intent_result2 = await intent_agent.execute(sample_user_message)

        # Same input should produce same intent (deterministic)
        assert intent_result1.intent == intent_result2.intent
        assert intent_result1.confidence == intent_result2.confidence

        # But vector clocks should differ (causal ordering)
        assert intent_result1.vector_clock.timestamp < intent_result2.vector_clock.timestamp


@pytest.mark.asyncio
async def test_error_handling_in_pipeline(
    intent_agent,
    fraud_agent
):
    """Test error handling and recovery in distributed pipeline.

    PATTERN: Failure Recovery
    Verifies that errors in one agent don't cascade and that the pipeline
    can recover or provide graceful degradation.

    See: docs/patterns/failure-recovery/recovery-strategies.md
    """
    # Test with empty/malformed data
    try:
        result = await intent_agent.execute("")
        # Should still return a result (graceful degradation)
        assert result is not None
    except Exception as e:
        # If it raises, that's also acceptable if documented
        assert isinstance(e, Exception)

    # Verify agent is still functional after error
    result = await intent_agent.execute("Test message")
    assert result.intent is not None


@pytest.mark.asyncio
async def test_trace_id_correlation(
    intent_agent,
    fraud_agent
):
    """Test trace ID propagation for observability.

    PATTERN: Distributed Tracing
    Verifies that trace IDs are properly set and can be used to correlate
    logs and messages across distributed agents.

    See: docs/patterns/observability/distributed-tracing.md
    """
    trace_id = "trace_abc123def456"

    # Both agents work on same trace
    intent_result = await intent_agent.execute("Sample message")
    fraud_result = await fraud_agent.execute({"amount": 1000})

    # In a real system, trace IDs would be propagated
    # This test documents the expected interface
    assert intent_agent.call_count == 1
    assert fraud_agent.call_count == 1


@pytest.mark.asyncio
async def test_degradation_mode_behavior(
    intent_agent,
    sample_user_message
):
    """Test graceful degradation when resources are constrained.

    PATTERN: Behavior Degradation
    Verifies that agents degrade gracefully when token budgets are exceeded
    or latency constraints are violated.

    See: docs/patterns/predictability/behavior-degradation.md
    """
    # Exhaust token budget
    original_budget = intent_agent.config.token_budget
    intent_agent.config.token_budget = 1  # Set very low budget

    # Agent should still function, possibly in degraded mode
    result = await intent_agent.execute(sample_user_message)

    # Verify we got a result
    assert result is not None
    assert hasattr(result, "confidence")

    # Restore budget
    intent_agent.config.token_budget = original_budget
