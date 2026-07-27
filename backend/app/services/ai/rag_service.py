"""
File: rag_service.py
Purpose:
    Provider-Agnostic Retrieval-Augmented Generation (RAG) Architecture for SentinelX Trust AI.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 2.0
"""

import re
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from schemas.ai import RAGChunk, RAGQueryRequest, RAGQueryResponse
from repositories.payment_repository import PaymentRepository

logger = logging.getLogger("backend.services.ai.rag_service")


class DocumentIngestor:
    """
    Transforms database payment records and metadata into structured RAG chunks.
    """

    @staticmethod
    def records_to_chunks(records: List[Dict[str, Any]]) -> List[RAGChunk]:
        """Converts raw or DB payment record dictionaries into searchable RAGChunks."""
        chunks = []
        for idx, rec in enumerate(records):
            site = rec.get("site", "unknown")
            p_name = rec.get("payment_name", "N/A")
            p_type = rec.get("payment_type", "N/A")
            country = rec.get("country", "N/A")
            currency = rec.get("currency", "N/A")
            support = rec.get("support_type", "") or rec.get("support_value", "") or "Standard support"
            bonus = rec.get("bonus_name", "") or "No active bonus"

            content = (
                f"Platform '{site}' supports payment method '{p_name}' (Category: {p_type}) "
                f"in country {country} with currency {currency}. Support protocol: {support}. Bonus offer: {bonus}."
            )

            chunk = RAGChunk(
                document_id=f"doc_{site}_{idx+1}",
                content=content,
                relevance_score=0.0,
                metadata={
                    "site": site,
                    "payment_name": p_name,
                    "payment_type": p_type,
                    "country": country,
                    "currency": currency
                }
            )
            chunks.append(chunk)
        return chunks


class RetrievalEngine:
    """
    Retrieves and ranks RAG chunks based on keyword matching and relevance scoring.
    Vendor-agnostic interface ready for vector search swap-in.
    """

    @staticmethod
    def retrieve_relevant(chunks: List[RAGChunk], query: str, top_k: int = 3, filter_site: Optional[str] = None) -> List[RAGChunk]:
        """Ranks documents against the user query using keyword frequency and exact-match weights."""
        query_words = set(re.findall(r'\w+', query.lower()))

        scored_chunks = []
        for chunk in chunks:
            if filter_site and chunk.metadata.get("site", "").lower() != filter_site.lower():
                continue

            content_lower = chunk.content.lower()
            matches = sum(1 for w in query_words if w in content_lower)

            # Extra weight for exact site match or payment method match in query
            site = chunk.metadata.get("site", "").lower()
            if site and site in query.lower():
                matches += 3

            score = min(1.0, round(matches / max(1, len(query_words) + 2), 2))
            if score > 0:
                chunk_copy = RAGChunk(
                    document_id=chunk.document_id,
                    content=chunk.content,
                    relevance_score=score,
                    metadata=chunk.metadata
                )
                scored_chunks.append(chunk_copy)

        # Sort by relevance score descending
        scored_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_chunks[:top_k]


class ContextBuilder:
    """
    Assembles retrieved chunks into bounded context windows for LLM prompts.
    """

    @staticmethod
    def build_context(chunks: List[RAGChunk]) -> str:
        """Formats retrieved chunks into clean numbered context blocks."""
        if not chunks:
            return "No relevant platform documents found."

        context_lines = ["--- BEGIN RETRIEVED CONTEXT ---"]
        for idx, chunk in enumerate(chunks, 1):
            context_lines.append(f"[{idx}] {chunk.content} (Relevance: {chunk.relevance_score})")
        context_lines.append("--- END RETRIEVED CONTEXT ---")

        return "\n".join(context_lines)


class PromptBuilder:
    """
    Externalized template renderer constructing provider-agnostic system/user prompts.
    """

    SYSTEM_TEMPLATE = (
        "You are SentinelX Trust AI Assistant. Use the provided context below to answer "
        "the user's query regarding betting platform payment methods, trust ratings, and compliance.\n\n"
        "CONTEXT:\n{context}\n\n"
        "USER QUERY: {query}\n\n"
        "ANSWER:"
    )

    @classmethod
    def build_prompt(cls, context: str, query: str) -> str:
        """Fills prompt template with context and query."""
        return cls.SYSTEM_TEMPLATE.format(context=context, query=query)


class ResponseFormatter:
    """
    Synthesizes and formats the RAG pipeline response payload.
    """

    @staticmethod
    def format_response(query: str, chunks: List[RAGChunk], prompt: str) -> RAGQueryResponse:
        """Synthesizes structured response including token estimates."""
        if chunks:
            top_doc = chunks[0]
            answer = f"Based on platform records: {top_doc.content}"
        else:
            answer = "No matching platform payment records found for the given query."

        # Token estimation heuristic (~4 chars per token)
        estimated_tokens = (len(prompt) + len(answer)) // 4

        return RAGQueryResponse(
            query=query,
            context_documents=chunks,
            formatted_prompt=prompt,
            synthesized_answer=answer,
            estimated_tokens=estimated_tokens
        )


class RAGService:
    """
    Main RAG Service orchestrator tying together Ingestion, Retrieval, Context, Prompting, and Formatting.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session

    def query(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """Executes the complete RAG query pipeline."""
        logger.info(f"Executing RAG query: '{request.query}' (top_k={request.top_k}, site={request.filter_site})")

        # 1. Fetch records
        records = []
        if self.db_session:
            repo = PaymentRepository(self.db_session)
            if request.filter_site:
                db_recs = repo.get_records_by_site(request.filter_site)
            else:
                db_recs, _ = repo.get_paginated_records(page=1, size=50)

            records = [
                {
                    "site": r.site,
                    "payment_type": r.payment_type,
                    "payment_name": r.payment_name,
                    "currency": r.currency,
                    "country": r.country,
                    "support_type": r.support_type,
                    "support_value": r.support_value,
                    "bonus_name": r.bonus_name,
                }
                for r in db_recs
            ]

        # Fallback sample data if DB is empty
        if not records:
            records = [
                {"site": "melbet", "payment_name": "Paytm", "payment_type": "e-wallet", "country": "IN", "currency": "INR", "support_type": "Live Chat", "bonus_name": "100% Welcome Bonus"},
                {"site": "melbet", "payment_name": "UPI", "payment_type": "e-wallet", "country": "IN", "currency": "INR", "support_type": "Live Chat", "bonus_name": "100% Welcome Bonus"},
                {"site": "10cric", "payment_name": "Net Banking", "payment_type": "bank_transfer", "country": "IN", "currency": "INR", "support_type": "Email", "bonus_name": "150% Deposit Match"},
                {"site": "22xbet", "payment_name": "Bitcoin", "payment_type": "crypto", "country": "BR", "currency": "BRL", "support_type": "Telegram", "bonus_name": "Crypto Bonus"}
            ]

        # 2. Ingest into chunks
        all_chunks = DocumentIngestor.records_to_chunks(records)

        # 3. Retrieve top relevant chunks
        relevant_chunks = RetrievalEngine.retrieve_relevant(
            chunks=all_chunks,
            query=request.query,
            top_k=request.top_k,
            filter_site=request.filter_site
        )

        # 4. Build context
        context_str = ContextBuilder.build_context(relevant_chunks)

        # 5. Build prompt
        prompt_str = PromptBuilder.build_prompt(context=context_str, query=request.query)

        # 6. Format and return response
        return ResponseFormatter.format_response(
            query=request.query,
            chunks=relevant_chunks,
            prompt=prompt_str
        )
