"""RAG module — factory for pluggable RAG retrievers.

Configuration:
    ``RAG_PROVIDER`` env var selects the backend (see ``RAGProvider`` enum).
    Defaults to ``local_rag`` when the env var is unset.
"""

from __future__ import annotations

import logging
from typing import Optional

from src.config.tools import SELECTED_RAG_PROVIDER, RAGProvider
from src.rag.base import BaseRAGRetriever, RetrievedDocument

logger = logging.getLogger(__name__)

_retriever: Optional[BaseRAGRetriever] = None


def get_rag_retriever() -> BaseRAGRetriever:
    """Return a singleton RAG retriever, creating it on first access.

    The backend is chosen via ``RAG_PROVIDER`` env var:
        - ``local_rag`` (default) — Qdrant + OpenAI embeddings
        - ``ragflow`` — RAGFlow API (future)
        - ``vikingdb_knowledge_base`` — VikingDB (future)
    """
    global _retriever
    if _retriever is not None:
        return _retriever

    provider = SELECTED_RAG_PROVIDER or RAGProvider.LOCAL_RAG.value
    logger.info("Initialising RAG retriever — provider=%s", provider)

    if provider == RAGProvider.LOCAL_RAG.value:
        from src.rag.local_rag import LocalRAGRetriever

        _retriever = LocalRAGRetriever()
    elif provider == RAGProvider.RAGFLOW.value:
        raise NotImplementedError("RAGFlow provider is not yet implemented")
    elif provider == RAGProvider.VIKINGDB_KNOWLEDGE_BASE.value:
        raise NotImplementedError("VikingDB provider is not yet implemented")
    else:
        logger.warning(
            "Unknown RAG provider '%s', falling back to local_rag", provider,
        )
        from src.rag.local_rag import LocalRAGRetriever

        _retriever = LocalRAGRetriever()

    return _retriever


__all__ = [
    "BaseRAGRetriever",
    "RetrievedDocument",
    "get_rag_retriever",
]
