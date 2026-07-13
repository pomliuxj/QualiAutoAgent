"""RAG Retriever — abstract base interface.

Implementations:
    - ``LocalRAGRetriever`` — ChromaDB-backed local vector store
    - Future: RAGFlow, VikingDB knowledge base connectors
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """A single document chunk returned by the retriever."""

    content: str
    """The text content of the retrieved chunk."""

    metadata: dict = field(default_factory=dict)
    """Source metadata: file name, page number, chunk index, etc."""

    score: float = 0.0
    """Relevance score (higher = more relevant)."""


class BaseRAGRetriever(ABC):
    """Abstract interface for a RAG document retriever.

    Subclasses implement ``search`` to return top-k relevant documents
    for a given query string.
    """

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Return the most relevant documents for the query."""
        ...

    @abstractmethod
    async def asearch(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Async variant of ``search``."""
        ...

    @abstractmethod
    def add_documents(self, docs_dir: str) -> int:
        """Index all supported documents from a directory. Returns count."""
        ...

    @abstractmethod
    def get_stats(self) -> dict:
        """Return retriever statistics: document count, chunk count, etc."""
        ...
