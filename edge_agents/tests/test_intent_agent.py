"""
Tests for Intent Detection Agent.

Tests verify:
1. Basic intent detection accuracy
2. Token budgeting enforcement
3. Graceful degradation to keyword matching
4. Reasoning and decision transparency
"""

import pytest
from edge_agents.intent_agent import (
    IntentDetectionAgent,
    IntentDetectionConfig,
    IntentCategory,
)


@pytest.fixture
def agent_normal():
    """Create agent with normal token budget."""
    config = IntentDetectionConfig(
        agent_id="test-agent-normal",
        token_budget=1000,
        intent_categories=[
            IntentCategory.PURCHASE.value,
            IntentCategory.SUPPORT.value,
            IntentCategory.INQUIRY.value,
            IntentCategory.FEEDBACK.value,
        ],
        confidence_threshold=0.7,
    )
    return IntentDetectionAgent(config)


@pytest.fixture
def agent_constrained():
    """Create agent with constrained token budget for testing degradation."""
    config = IntentDetectionConfig(
        agent_id="test-agent-constrained",
        token_budget=5,  # Very small budget to trigger degradation
        intent_categories=[
            IntentCategory.PURCHASE.value,
            IntentCategory.SUPPORT.value,
            IntentCategory.INQUIRY.value,
            IntentCategory.FEEDBACK.value,
        ],
        confidence_threshold=0.7,
    )
    return IntentDetectionAgent(config)


@pytest.mark.asyncio
async def test_intent_detection_purchase(agent_normal):
    """
    Test intent detection for purchase intent.

    Verifies that "buy laptop" is correctly identified as purchase
    intent with confidence > 0.7.
    """
    message = "I want to buy a laptop"
    result = await agent_normal.execute(message)

    assert result.intent == IntentCategory.PURCHASE.value
    assert result.confidence > 0.7
    assert not result.degraded
    assert result.tokens_consumed > 0
    assert "laptop" in result.reasoning.lower()


@pytest.mark.asyncio
async def test_intent_detection_support(agent_normal):
    """
    Test intent detection for support intent.

    Verifies that "problem with order" is correctly identified as support
    intent with confidence > 0.7.
    """
    message = "I have a problem with my order. It's broken."
    result = await agent_normal.execute(message)

    assert result.intent == IntentCategory.SUPPORT.value
    assert result.confidence > 0.7
    assert not result.degraded
    assert result.tokens_consumed > 0


@pytest.mark.asyncio
async def test_intent_detection_inquiry(agent_normal):
    """
    Test intent detection for inquiry intent.

    Verifies that questions are correctly identified as inquiry intent.
    """
    message = "What are the product specifications?"
    result = await agent_normal.execute(message)

    assert result.intent == IntentCategory.INQUIRY.value
    assert result.confidence > 0.5
    assert not result.degraded


@pytest.mark.asyncio
async def test_intent_detection_feedback(agent_normal):
    """
    Test intent detection for feedback intent.

    Verifies that feedback is correctly identified.
    """
    message = "I love this product! Great quality."
    result = await agent_normal.execute(message)

    assert result.intent == IntentCategory.FEEDBACK.value
    assert result.confidence > 0.5
    assert not result.degraded


@pytest.mark.asyncio
async def test_token_budget_enforcement(agent_constrained):
    """
    Test token budget enforcement and degradation.

    With budget=5, verify:
    1. First call uses tokens (within or near budget)
    2. Second call degrades to keyword matching (budget exceeded)
    3. Degraded result has lower confidence than normal inference would
    """
    # First call: should succeed normally
    message1 = "buy laptop"
    result1 = await agent_constrained.execute(message1)
    # First call not degraded
    assert result1.degraded is False

    # Make a longer message to guarantee degradation on second call
    message2 = "I would like to purchase a new laptop computer with specifications including processor and memory and storage and graphics card"
    result2 = await agent_constrained.execute(message2)

    # Second call should degrade (budget is exhausted)
    assert result2.degraded is True
    # Degraded confidence should be lower than normal mode would be
    assert result2.confidence < 0.7  # Degraded mode caps at lower confidence
    assert "DEGRADED" in result2.reasoning.upper()


@pytest.mark.asyncio
async def test_reasoning_transparency(agent_normal):
    """
    Test that reasoning is transparent and informative.

    PATTERN: Understanding Model Decisions
    Verifies that the agent provides reasoning for its decisions.
    """
    message = "I need help with my device"
    result = await agent_normal.execute(message)

    # Reasoning should mention the intent
    assert result.intent in result.reasoning.lower()
    # Should mention confidence
    assert "confidence" in result.reasoning.lower()
    # Should reference the input
    assert "device" in result.reasoning.lower()


@pytest.mark.asyncio
async def test_vector_clock_increment(agent_normal):
    """
    Test that vector clock increments with each call.

    PATTERN: Causality tracking via vector clocks.
    """
    await agent_normal.execute("buy something")
    vc1 = agent_normal.vector_clock.timestamp

    await agent_normal.execute("need help")
    vc2 = agent_normal.vector_clock.timestamp

    assert vc2 > vc1
    assert vc2 == vc1 + 1


@pytest.mark.asyncio
async def test_token_usage_tracking(agent_normal):
    """
    Test that token usage is properly tracked.

    PATTERN: Token Budgeting
    Verifies token usage accumulation and summary.
    """
    await agent_normal.execute("buy laptop")
    await agent_normal.execute("need support")

    summary = agent_normal.get_token_usage_summary()

    assert summary["total_calls"] == 2
    assert summary["total_tokens_used"] > 0
    assert summary["token_budget"] == 1000
    assert summary["budget_utilization"] >= 0
    assert summary["budget_utilization"] <= 1.0


@pytest.mark.asyncio
async def test_multiple_calls_within_budget(agent_normal):
    """
    Test that multiple calls work correctly within budget.

    Verifies that the agent handles multiple sequential calls.
    """
    messages = [
        "buy a phone",
        "need help with order",
        "what is the price?",
        "great product!",
    ]

    results = []
    for msg in messages:
        result = await agent_normal.execute(msg)
        results.append(result)

    # All results should be valid
    assert len(results) == 4
    assert all(r.intent is not None for r in results)
    assert all(r.tokens_consumed > 0 for r in results)


@pytest.mark.asyncio
async def test_degradation_reduces_token_consumption(agent_constrained):
    """
    Test that degraded mode uses fewer tokens than normal mode.

    PATTERN: Behavior Degradation
    Verifies that fallback mode is more resource-efficient.
    """
    # Use very long messages to trigger degradation
    long_message = "I want to purchase " + ("something " * 50)

    result1 = await agent_constrained.execute(long_message)
    result2 = await agent_constrained.execute(long_message)

    # If result2 is degraded, it should use fewer tokens
    if result2.degraded:
        assert result2.tokens_consumed <= result1.tokens_consumed


@pytest.mark.asyncio
async def test_confidence_vs_degradation(agent_normal, agent_constrained):
    """
    Test that degraded results have lower confidence.

    PATTERN: Understanding Model Decisions
    Verifies that confidence scores reflect computation method.
    """
    message = "buy something"

    # Normal execution
    result_normal = await agent_normal.execute(message)

    # Get another agent that will eventually degrade
    config = IntentDetectionConfig(
        agent_id="test-agent-degrad",
        token_budget=10,
        confidence_threshold=0.7,
    )
    agent = IntentDetectionAgent(config)

    # Fill budget
    for i in range(2):
        await agent.execute("long message " + ("test " * 100))

    # This should degrade
    result_degraded = await agent.execute(message)

    # Degraded should have lower confidence
    assert result_degraded.degraded
    assert result_degraded.confidence < result_normal.confidence


@pytest.mark.asyncio
async def test_empty_message(agent_normal):
    """
    Test handling of edge case: empty message.
    """
    result = await agent_normal.execute("")

    assert result.intent is not None
    assert result.confidence >= 0.0
    # Empty message should not crash


@pytest.mark.asyncio
async def test_long_message(agent_normal):
    """
    Test handling of very long message.

    Verifies token estimation works for long inputs.
    """
    long_message = "I want to buy a laptop with the following specifications: " + (
        "high performance processor, "
        "large display, "
        "good battery life, "
        "lightweight, "
        "affordable price, "
    ) * 10

    result = await agent_normal.execute(long_message)

    assert result.intent is not None
    assert result.tokens_consumed > 0
    # Longer message should consume more tokens
    assert result.tokens_consumed > len("buy") // 4
