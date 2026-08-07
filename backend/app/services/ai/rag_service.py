"""
File: rag_service.py
Purpose:
    Provider-Agnostic Retrieval-Augmented Generation (RAG) Architecture with Gold Layer integration.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import re
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from schemas.ai import RAGChunk, RAGQueryRequest, RAGQueryResponse
from repositories.payment_repository import PaymentRepository
from repositories.gold_repository import GoldRepository

logger = logging.getLogger("backend.services.ai.rag_service")


class DocumentIngestor:
    """
    Transforms database payment records, Gold platform analytics, and payment insights into RAG chunks.
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

    @staticmethod
    def gold_analytics_to_chunks(analytics_list: List[Any]) -> List[RAGChunk]:
        """Converts GoldPlatformAnalytics records into high-level RAGChunks."""
        chunks = []
        for idx, g in enumerate(analytics_list):
            content = (
                f"Gold Summary for Platform '{g.site}': Trust Score is {g.trust_score}/100 ({g.trust_level} Risk Level) "
                f"with {g.confidence_score*100:.0f}% data confidence. Total payment methods: {g.total_payment_methods} ({g.active_payment_methods} active). "
                f"Top payment options: {', '.join(g.top_payment_methods or [])}. Risk Overview: {g.risk_summary}"
            )
            chunk = RAGChunk(
                document_id=f"gold_doc_{g.site}_{idx+1}",
                content=content,
                relevance_score=0.0,
                metadata={
                    "site": g.site,
                    "trust_score": g.trust_score,
                    "trust_level": g.trust_level,
                    "type": "gold_summary"
                }
            )
            chunks.append(chunk)
        return chunks


class RetrievalEngine:
    """
    Retrieves and ranks RAG chunks based on keyword matching and relevance scoring.
    """

    @staticmethod
    def retrieve_relevant(chunks: List[RAGChunk], query: str, top_k: int = 3, filter_site: Optional[str] = None) -> List[RAGChunk]:
        query_words = set(re.findall(r'\w+', query.lower()))

        scored_chunks = []
        for chunk in chunks:
            if filter_site and chunk.metadata.get("site", "").lower() != filter_site.lower():
                continue

            content_lower = chunk.content.lower()
            matches = sum(1 for w in query_words if w in content_lower)

            site = chunk.metadata.get("site", "").lower()
            if site and site in query.lower():
                matches += 3

            if chunk.metadata.get("type") == "gold_summary":
                matches += 2  # Prioritize curated Gold summaries

            score = min(1.0, round(matches / max(1, len(query_words) + 2), 2))
            if score > 0:
                chunk_copy = RAGChunk(
                    document_id=chunk.document_id,
                    content=chunk.content,
                    relevance_score=score,
                    metadata=chunk.metadata
                )
                scored_chunks.append(chunk_copy)

        scored_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_chunks[:top_k]


class ContextBuilder:
    @staticmethod
    def build_context(chunks: List[RAGChunk]) -> str:
        if not chunks:
            return "No relevant platform documents found."

        context_lines = ["--- BEGIN RETRIEVED CONTEXT ---"]
        for idx, chunk in enumerate(chunks, 1):
            context_lines.append(f"[{idx}] {chunk.content} (Relevance: {chunk.relevance_score})")
        context_lines.append("--- END RETRIEVED CONTEXT ---")

        return "\n".join(context_lines)


class PromptBuilder:
    SYSTEM_TEMPLATE = (
        "You are SentinelX Trust AI Assistant. Use the provided context below to answer "
        "the user's query regarding betting platform payment methods, trust ratings, and compliance.\n\n"
        "CONTEXT:\n{context}\n\n"
        "USER QUERY: {query}\n\n"
        "ANSWER:"
    )

    @classmethod
    def build_prompt(cls, context: str, query: str) -> str:
        return cls.SYSTEM_TEMPLATE.format(context=context, query=query)


class ResponseFormatter:
    @staticmethod
    def format_response(query: str, chunks: List[RAGChunk], prompt: str) -> RAGQueryResponse:
        if chunks:
            top_doc = chunks[0]
            answer = f"Based on platform records: {top_doc.content}"
        else:
            answer = "No matching platform payment records found for the given query."

        estimated_tokens = (len(prompt) + len(answer)) // 4

        return RAGQueryResponse(
            query=query,
            context_documents=chunks,
            formatted_prompt=prompt,
            synthesized_answer=answer,
            estimated_tokens=estimated_tokens
        )


class RAGService:
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session

    def query(self, request: RAGQueryRequest) -> RAGQueryResponse:
        logger.info(f"Executing Gold-integrated RAG query: '{request.query}' (top_k={request.top_k}, site={request.filter_site})")

        records = []
        gold_chunks = []
        if self.db_session:
            gold_repo = GoldRepository(self.db_session)
            if request.filter_site:
                g_analytics = gold_repo.get_platform_analytics(request.filter_site)
                if g_analytics:
                    gold_chunks = DocumentIngestor.gold_analytics_to_chunks([g_analytics])
            else:
                g_list, _ = gold_repo.list_platform_analytics(page=1, size=20)
                if g_list:
                    gold_chunks = DocumentIngestor.gold_analytics_to_chunks(g_list)

            payment_repo = PaymentRepository(self.db_session)
            if request.filter_site:
                db_recs = payment_repo.get_records_by_site(request.filter_site)
            else:
                db_recs, _ = payment_repo.get_paginated_records(page=1, size=50)

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

        if not records and not gold_chunks:
            records = [
                {"site": "melbet", "payment_name": "Paytm", "payment_type": "e-wallet", "country": "IN", "currency": "INR", "support_type": "Live Chat", "bonus_name": "100% Welcome Bonus"},
                {"site": "melbet", "payment_name": "UPI", "payment_type": "e-wallet", "country": "IN", "currency": "INR", "support_type": "Live Chat", "bonus_name": "100% Welcome Bonus"},
                {"site": "10cric", "payment_name": "Net Banking", "payment_type": "bank_transfer", "country": "IN", "currency": "INR", "support_type": "Email", "bonus_name": "150% Deposit Match"},
                {"site": "22xbet", "payment_name": "Bitcoin", "payment_type": "crypto", "country": "BR", "currency": "BRL", "support_type": "Telegram", "bonus_name": "Crypto Bonus"}
            ]

        record_chunks = DocumentIngestor.records_to_chunks(records)
        all_chunks = gold_chunks + record_chunks

        relevant_chunks = RetrievalEngine.retrieve_relevant(
            chunks=all_chunks,
            query=request.query,
            top_k=request.top_k,
            filter_site=request.filter_site
        )

        context_str = ContextBuilder.build_context(relevant_chunks)
        prompt_str = PromptBuilder.build_prompt(context=context_str, query=request.query)

        return ResponseFormatter.format_response(
            query=request.query,
            chunks=relevant_chunks,
            prompt=prompt_str
        )
