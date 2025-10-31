"""LangGraph RAG agent with route→retrieve→answer→verify→finalize flow."""

import json
import re
from typing import Any

import weave
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from rag_health_core import QueryResponse, RAGPrompts, RAGState, Settings
from rag_health_retrieval import EmbeddingService, RedisClient


class RAGAgent(weave.Model):
    """LangGraph-based RAG agent for drug label Q&A with Weave tracing."""

    settings: Settings
    redis_client: RedisClient
    embedding_service: EmbeddingService
    llm: ChatOpenAI
    graph: Any

    def __init__(self, settings: Settings) -> None:
        """Initialize agent with Redis and LLM clients."""
        super().__init__()
        self.settings = settings
        self.redis_client = RedisClient(settings)
        self.embedding_service = EmbeddingService(settings)
        self.llm = ChatOpenAI(
            model=settings.openai_chat_model,
            api_key=settings.openai_api_key,
            temperature=0.0,
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        """Build LangGraph state machine."""
        workflow = StateGraph(RAGState)

        workflow.add_node("route_intent", self._route_intent)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("answer", self._answer)
        workflow.add_node("verify", self._verify)
        workflow.add_node("finalize", self._finalize)

        workflow.set_entry_point("route_intent")
        workflow.add_edge("route_intent", "retrieve")
        workflow.add_edge("retrieve", "answer")
        workflow.add_edge("answer", "verify")
        workflow.add_edge("verify", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    @weave.op()
    async def query(self, query: str, drug: str | None = None, top_k: int = 6) -> QueryResponse:
        """Execute RAG query through the agent graph.

        This method is traced by Weave and will log:
        - Input: query, drug, top_k
        - Output: QueryResponse with answer, confidence, contexts
        - Latency: End-to-end execution time
        - All nested operations (route, retrieve, answer, verify, finalize)
        """
        initial_state: RAGState = {
            "query": query,
            "drug": drug,
            "target_sections": [],
            "ctx": [],
            "draft": "",
            "confidence": 0.0,
            "answer": "",
            "error": None,
        }

        final_state = await self.graph.ainvoke(initial_state)

        return QueryResponse(
            answer=final_state["answer"],
            confidence=final_state["confidence"],
            contexts=final_state["ctx"][:top_k],
            drug=final_state.get("drug"),
        )

    @weave.op()
    def _route_intent(self, state: RAGState) -> RAGState:
        """Node: Extract drug and target sections from query."""
        query = state["query"]

        messages = [
            SystemMessage(content=RAGPrompts.INTENT_SYSTEM),
            HumanMessage(content=RAGPrompts.format_intent_prompt(query)),
        ]

        response = self.llm.invoke(messages)
        content = response.content

        # Parse JSON response
        try:
            parsed = json.loads(content) if isinstance(content, str) else {}
            drug = parsed.get("drug") or state.get("drug")
            sections = parsed.get("sections", [])
        except Exception:
            drug = state.get("drug")
            sections = []

        # Default to common sections if empty
        if not sections:
            sections = [
                "DOSAGE_AND_ADMINISTRATION",
                "CONTRAINDICATIONS",
                "WARNINGS_AND_PRECAUTIONS",
                "ADVERSE_REACTIONS",
            ]

        state["drug"] = drug
        state["target_sections"] = sections
        return state

    @weave.op()
    def _retrieve(self, state: RAGState) -> RAGState:
        """Node: Retrieve relevant contexts from Redis."""
        query = state["query"]
        drug = state.get("drug")
        target_sections = state.get("target_sections", [])

        # Generate query embedding
        query_emb = self.embedding_service.embed(query)

        # Search with filters
        contexts = self.redis_client.search(
            query_embedding=query_emb,
            top_k=self.settings.retrieval_top_k,
            drug_filter=drug,
            section_filter=target_sections if target_sections else None,
        )

        state["ctx"] = contexts
        return state

    @weave.op()
    def _answer(self, state: RAGState) -> RAGState:
        """Node: Generate answer from contexts."""
        query = state["query"]
        contexts = state["ctx"]

        if not contexts:
            state["draft"] = "Not in the label context provided."
            state["confidence"] = 0.0
            return state

        # Format contexts for prompt
        ctx_dicts = [
            {
                "section": ctx.section,
                "text": ctx.text,
                "citation": ctx.citation(),
            }
            for ctx in contexts
        ]

        messages = [
            SystemMessage(content=RAGPrompts.SYSTEM),
            HumanMessage(content=RAGPrompts.format_user_prompt(query, ctx_dicts)),
        ]

        response = self.llm.invoke(messages)
        draft = response.content if isinstance(response.content, str) else ""

        state["draft"] = draft
        return state

    @weave.op()
    def _verify(self, state: RAGState) -> RAGState:
        """Node: Verify answer has citations and reasonable confidence."""
        draft = state["draft"]
        contexts = state["ctx"]

        # Check for citations
        citation_pattern = r"\[Section:.*?\]\s*\(.*?#section=.*?\)"
        citations_found = re.findall(citation_pattern, draft)

        if citations_found:
            # High confidence if citations present
            confidence = 0.9
        elif contexts:
            # Medium confidence if context exists but no citations
            confidence = 0.6
        else:
            # Low confidence if no context
            confidence = 0.2

        # If below threshold and no citations, add fallback
        if confidence < self.settings.confidence_threshold and not citations_found:
            draft = "Not in the label context provided. Please refine your query or specify a drug name."

        state["confidence"] = confidence
        state["answer"] = draft
        return state

    @weave.op()
    def _finalize(self, state: RAGState) -> RAGState:
        """Node: Add disclaimer to final answer."""
        answer = state["answer"]

        # Add disclaimer if answer is substantive
        if answer and "Not in the label context provided" not in answer:
            answer += "\n\n⚠️ Not medical advice. Verify via linked label."

        state["answer"] = answer
        return state
