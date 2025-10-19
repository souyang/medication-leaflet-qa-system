"""Prompt templates for RAG pipeline."""


class RAGPrompts:
    """Centralized prompt templates with citation enforcement."""

    SYSTEM = """You answer only from the CONTEXT, which comes from FDA drug labels (SPL).
Every factual statement must include a citation: [Section: <name>] (<url>#section=<id>).
If the answer is not in CONTEXT, say: "Not in the label context provided."
Keep answers concise; list key numbers (dose, interval, adjustments) first."""

    USER_TEMPLATE = """Question: {query}

CONTEXT (≤{count} chunks):
{context}

Answer:"""

    INTENT_SYSTEM = """Extract the drug name (if any) and map the question to relevant FDA label sections.

Valid sections:
- DOSAGE_AND_ADMINISTRATION
- CONTRAINDICATIONS
- WARNINGS_AND_PRECAUTIONS
- ADVERSE_REACTIONS
- USE_IN_SPECIFIC_POPULATIONS
- HOW_SUPPLIED_STORAGE_AND_HANDLING
- PATIENT_COUNSELING_INFORMATION
- INDICATIONS_AND_USAGE
- CLINICAL_PHARMACOLOGY

Return JSON: {{"drug": "<name or null>", "sections": ["<section>"]}}.
If unclear, return all sections."""

    INTENT_USER_TEMPLATE = """Question: {query}"""

    @staticmethod
    def format_user_prompt(query: str, contexts: list[dict[str, str]]) -> str:
        """Format user prompt with query and contexts."""
        context_text = "\n\n---\n\n".join(
            f"[{i+1}] Section: {ctx['section']}\n{ctx['text']}\nCitation: {ctx['citation']}"
            for i, ctx in enumerate(contexts)
        )
        return RAGPrompts.USER_TEMPLATE.format(
            query=query, count=len(contexts), context=context_text or "(No context provided)"
        )

    @staticmethod
    def format_intent_prompt(query: str) -> str:
        """Format intent routing prompt."""
        return RAGPrompts.INTENT_USER_TEMPLATE.format(query=query)
