"""Tests for prompt templates."""

from rag_health_core import RAGPrompts


def test_format_user_prompt() -> None:
    """Test user prompt formatting with contexts."""
    contexts = [
        {
            "section": "DOSAGE_AND_ADMINISTRATION",
            "text": "Start with 500 mg twice daily.",
            "citation": "[Section: DOSAGE] (url#section=34068-7)",
        },
        {
            "section": "CONTRAINDICATIONS",
            "text": "Do not use in severe renal impairment.",
            "citation": "[Section: CONTRAINDICATIONS] (url#section=34070-3)",
        },
    ]

    prompt = RAGPrompts.format_user_prompt("What is the dose?", contexts)

    assert "What is the dose?" in prompt
    assert "Start with 500 mg twice daily." in prompt
    assert "Do not use in severe renal impairment." in prompt
    assert "[Section: DOSAGE]" in prompt
    assert "CONTEXT (≤2 chunks)" in prompt


def test_format_user_prompt_empty_contexts() -> None:
    """Test prompt with no contexts."""
    prompt = RAGPrompts.format_user_prompt("Test query", [])
    assert "Test query" in prompt
    assert "(No context provided)" in prompt


def test_format_intent_prompt() -> None:
    """Test intent routing prompt."""
    prompt = RAGPrompts.format_intent_prompt("What are the side effects?")
    assert "What are the side effects?" in prompt
