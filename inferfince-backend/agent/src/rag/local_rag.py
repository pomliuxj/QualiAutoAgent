"""Local RAG Retriever — Qdrant-backed vector store with OpenAI-compatible embeddings.

Supports two modes:
    - **Local disk mode** (default): persistent file-based storage, no server needed
    - **Server mode**: connect to a remote Qdrant server via URL

Configuration (environment variables):
    ``RAG_DOCS_DIR`` — Directory containing documents to index (.md, .txt, .pdf)
    ``QDRANT_URL`` — Remote Qdrant server URL (omit for local disk mode)
    ``QDRANT_PATH`` — Local persistence path (default: ./qdrant_db)
    ``QDRANT_COLLECTION`` — Collection name (default: rag_docs)
    ``RAG_TOP_K`` — Default number of chunks to retrieve (default: 5)
    ``RAG_CHUNK_SIZE`` — Characters per chunk (default: 1000)
    ``RAG_CHUNK_OVERLAP`` — Overlap between chunks (default: 200)
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import List

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.embeddings import Embeddings
from openai import OpenAI
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    DirectoryLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore

from src.rag.base import BaseRAGRetriever, RetrievedDocument

logger = logging.getLogger(__name__)


# ── DashScope-compatible Embeddings ──────────────────────────────────────────

class DashScopeEmbeddings(Embeddings):
    """OpenAI-protocol embeddings client for DashScope (阿里云百炼).

    DashScope limits embedding batches to 10 texts per request.
    This wrapper transparently splits larger batches.
    """

    BATCH_SIZE = 10

    def __init__(self, model: str, api_key: str, base_url: str, **kwargs):
        self.model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url, **kwargs)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i : i + self.BATCH_SIZE]
            resp = self._client.embeddings.create(model=self.model, input=batch)
            vectors.extend(d.embedding for d in resp.data)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        resp = self._client.embeddings.create(model=self.model, input=text)
        return resp.data[0].embedding


# ── Defaults ─────────────────────────────────────────────────────────────────
DEFAULT_QDRANT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "qdrant")
DEFAULT_COLLECTION = "rag_docs"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_TOP_K = 5


def _resolve_path(path: str) -> str:
    """Resolve a path relative to the project root."""
    p = Path(path)
    if p.is_absolute():
        return str(p)
    # Resolve relative to the agent package root
    root = Path(__file__).resolve().parent.parent.parent.parent
    return str(root / path)


class LocalRAGRetriever(BaseRAGRetriever):
    """Qdrant + OpenAI embeddings based local RAG retriever.

    In local disk mode, Qdrant stores vectors on disk — no separate server
    process required.  For production deployments, point ``QDRANT_URL`` at a
    Qdrant server instance.

    Usage::

        retriever = LocalRAGRetriever()
        retriever.add_documents("./docs")
        docs = retriever.search("How to create test cases?", top_k=3)
    """

    def __init__(
        self,
        docs_dir: str | None = None,
        qdrant_url: str | None = None,
        qdrant_path: str | None = None,
        collection_name: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        embedding_model: str | None = None,
    ):
        self._docs_dir = _resolve_path(
            docs_dir or os.getenv("RAG_DOCS_DIR", "./docs")
        )
        self._chunk_size = chunk_size or int(
            os.getenv("RAG_CHUNK_SIZE", str(DEFAULT_CHUNK_SIZE))
        )
        self._chunk_overlap = chunk_overlap or int(
            os.getenv("RAG_CHUNK_OVERLAP", str(DEFAULT_CHUNK_OVERLAP))
        )
        self._top_k = int(os.getenv("RAG_TOP_K", str(DEFAULT_TOP_K)))
        self._collection_name = collection_name or os.getenv(
            "QDRANT_COLLECTION", DEFAULT_COLLECTION
        )

        # Embeddings — reuse the project's LLM configuration.
        # Priority: RAG_EMBEDDING_MODEL > BASIC_MODEL env vars > OPENAI_* defaults
        self._embedding_model = embedding_model or os.getenv(
            "RAG_EMBEDDING_MODEL", "text-embedding-3-small"
        )
        self._embeddings = self._create_embeddings()

        # Qdrant client — local disk mode or remote server
        self._qdrant_url = qdrant_url or os.getenv("QDRANT_URL")
        self._qdrant_path = _resolve_path(
            qdrant_path or os.getenv("QDRANT_PATH", "./qdrant_db")
        )

        if self._qdrant_url:
            logger.info("Connecting to Qdrant server at %s", self._qdrant_url)
            self._client = QdrantClient(url=self._qdrant_url)
        else:
            os.makedirs(self._qdrant_path, exist_ok=True)
            logger.info("Using local Qdrant storage at %s", self._qdrant_path)
            self._client = QdrantClient(path=self._qdrant_path)

        self._vectorstore: QdrantVectorStore | None = None
        self._init_store()

    # ── Embeddings factory ────────────────────────────────────────────────────

    @staticmethod
    def _create_embeddings() -> DashScopeEmbeddings:
        """Create a DashScope-compatible Embeddings instance from YAML config.

        Primary source: ``EMBEDDING_MODEL`` section in conf_<env>.yaml.
        ``api_key`` / ``base_url`` fall back to ``BASIC_MODEL`` when omitted.
        """
        from src.config import YAML_CONFIG

        embed_conf = YAML_CONFIG.get("EMBEDDING_MODEL", {})
        basic_conf = YAML_CONFIG.get("BASIC_MODEL", {})

        model = embed_conf.get("model") or os.getenv("RAG_EMBEDDING_MODEL") or "text-embedding-v3"
        api_key = embed_conf.get("api_key") or basic_conf.get("api_key", "")
        base_url = embed_conf.get("base_url") or basic_conf.get("base_url", "")

        # Env var overrides (highest priority)
        if os.getenv("RAG_EMBEDDING_API_KEY"):
            api_key = os.getenv("RAG_EMBEDDING_API_KEY")
        if os.getenv("RAG_EMBEDDING_BASE_URL"):
            base_url = os.getenv("RAG_EMBEDDING_BASE_URL")
        if not api_key:
            api_key = os.getenv("BASIC_MODEL__api_key") or os.getenv("OPENAI_API_KEY", "")
        if not base_url:
            base_url = os.getenv("BASIC_MODEL__base_url") or os.getenv("OPENAI_BASE_URL", "")

        logger.info(
            "Embeddings: model=%s base_url=%s api_key=%s",
            model, base_url or "(default)", "***" if api_key else "(not set)",
        )
        return DashScopeEmbeddings(model=model, api_key=api_key, base_url=base_url)

    # ── Vector store lifecycle ───────────────────────────────────────────────

    def _collection_exists(self) -> bool:
        """Check whether our collection already exists."""
        try:
            collections = self._client.get_collections()
            names = [c.name for c in collections.collections]
            return self._collection_name in names
        except Exception:
            return False

    def _get_indexed_sources(self) -> set[str]:
        """Return already-indexed source files from a local tracking file."""
        import json as _json
        tracking_file = os.path.join(os.path.dirname(self._qdrant_path), "_indexed_files.json")
        try:
            if os.path.exists(tracking_file):
                with open(tracking_file, "r", encoding="utf-8") as f:
                    sources = set(_json.load(f))
                logger.info("Found %d indexed source files in tracking file", len(sources))
                return sources
        except Exception:
            pass
        return set()

    def _save_indexed_sources(self, sources: set[str]) -> None:
        """Persist indexed source files to a local tracking file."""
        import json as _json
        tracking_file = os.path.join(os.path.dirname(self._qdrant_path), "_indexed_files.json")
        try:
            all_sources = self._get_indexed_sources() | sources
            with open(tracking_file, "w", encoding="utf-8") as f:
                _json.dump(sorted(all_sources), f, ensure_ascii=False)
        except Exception as e:
            logger.warning("Failed to save indexed sources: %s", e)

    def _init_store(self) -> None:
        """Initialise or load the Qdrant vector store, with incremental indexing."""
        try:
            if self._collection_exists():
                self._vectorstore = QdrantVectorStore(
                    client=self._client,
                    collection_name=self._collection_name,
                    embedding=self._embeddings,
                )
                count = self._client.count(
                    collection_name=self._collection_name
                ).count
                logger.info(
                    "Qdrant loaded (%d chunks in collection '%s')",
                    count, self._collection_name,
                )
                # Always check for new / updated documents
                indexed = self.add_documents(self._docs_dir)
                if indexed:
                    logger.info("Incremental index: +%d new chunks from %s", indexed, self._docs_dir)
            else:
                # No collection yet — create it, then index all documents.
                sample = self._embeddings.embed_query("init")
                self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=VectorParams(
                        size=len(sample),
                        distance=Distance.COSINE,
                    ),
                )
                self._vectorstore = QdrantVectorStore(
                    client=self._client,
                    collection_name=self._collection_name,
                    embedding=self._embeddings,
                )
                logger.info(
                    "Qdrant collection '%s' created (dim=%d)",
                    self._collection_name, len(sample),
                )
                indexed = self.add_documents(self._docs_dir)
                if indexed:
                    logger.info("Initial index: %d chunks from %s", indexed, self._docs_dir)
                else:
                    logger.info(
                        "No documents found in %s — knowledge base is empty.",
                        self._docs_dir,
                    )
        except Exception as exc:
            logger.warning(
                "Failed to init Qdrant: %s — will retry on first access", exc,
            )
            self._vectorstore = None

    def _ensure_store(self) -> QdrantVectorStore:
        """Lazy-init the vector store on first access.

        No collection I/O happens before the first search or add_documents call.
        """
        if self._vectorstore is not None:
            return self._vectorstore
        self._init_store()
        if self._vectorstore is None:
            # _init_store failed — create a bare store, search will error gracefully
            self._vectorstore = QdrantVectorStore(
                client=self._client,
                collection_name=self._collection_name,
                embedding=self._embeddings,
            )
        return self._vectorstore

    # ── Document ingestion ───────────────────────────────────────────────────

    def add_documents(self, docs_dir: str | None = None) -> int:
        """Scan a directory and index all supported documents.

        Supported formats: ``.md``, ``.txt``, ``.pdf``.
        Documents are split into chunks and added to the Qdrant collection.

        Returns the number of newly added chunks.
        """
        target = _resolve_path(docs_dir or self._docs_dir)
        if not os.path.isdir(target):
            logger.warning("RAG docs directory not found: %s", target)
            return 0

        loaders = {
            "**/*.md":  (TextLoader,   {"encoding": "utf-8"}),
            "**/*.txt": (TextLoader,   {"encoding": "utf-8"}),
            "**/*.pdf": (PyPDFLoader,  {}),
        }

        all_docs = []
        for glob_pattern, (loader_cls, kwargs) in loaders.items():
            try:
                loader = DirectoryLoader(
                    target,
                    glob=glob_pattern,
                    loader_cls=loader_cls,
                    loader_kwargs=kwargs if kwargs else None,
                    show_progress=False,
                    silent_errors=True,
                )
                docs = loader.load()
                logger.info("Loaded %d documents matching %s", len(docs), glob_pattern)
                all_docs.extend(docs)
            except Exception as exc:
                logger.warning("Failed to load %s: %s", glob_pattern, exc)

        if not all_docs:
            logger.info("No documents found in %s", target)
            return 0

        # Skip already-indexed source files (incremental indexing)
        indexed_sources = self._get_indexed_sources()
        new_docs = [d for d in all_docs
                     if d.metadata.get("source", "") not in indexed_sources]
        skipped = len(all_docs) - len(new_docs)
        if skipped:
            logger.info("Skipped %d already-indexed files", skipped)
        if not new_docs:
            logger.info("All %d documents already indexed — nothing to add", len(all_docs))
            return 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            separators=["\n\n", "\n", "。", ".", " ", ""],
        )
        chunks = splitter.split_documents(new_docs)
        logger.info(
            "Split %d new docs into %d chunks (size=%d, overlap=%d)",
            len(new_docs), len(chunks), self._chunk_size, self._chunk_overlap,
        )

        # _ensure_store() will create the collection if needed (via _init_store)
        store = self._ensure_store()
        store.add_documents(chunks)
        # Track newly indexed source files
        new_sources = {d.metadata.get("source", "") for d in new_docs if d.metadata.get("source")}
        self._save_indexed_sources(new_sources)
        logger.info("Added %d new chunks to Qdrant", len(chunks))
        return len(chunks)

    # ── Retrieval ────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int | None = None) -> List[RetrievedDocument]:
        """Search the Qdrant vector store for relevant chunks."""
        k = top_k or self._top_k
        store = self._ensure_store()

        try:
            results = store.similarity_search_with_score(query, k=k)
        except Exception as exc:
            logger.error("Qdrant vector search failed: %s", exc)
            return []

        return [
            RetrievedDocument(
                content=doc.page_content,
                metadata=doc.metadata,
                score=score,
            )
            for doc, score in results
        ]

    async def asearch(self, query: str, top_k: int | None = None) -> List[RetrievedDocument]:
        """Async wrapper — runs search in a thread pool."""
        return await asyncio.to_thread(self.search, query, top_k)

    # ── Stats ────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Return basic statistics about the vector store."""
        try:
            count_info = self._client.count(
                collection_name=self._collection_name
            )
            count = count_info.count
        except Exception:
            count = 0
        return {
            "provider": "qdrant" + ("_local" if not self._qdrant_url else "_server"),
            "chunk_count": count,
            "collection": self._collection_name,
            "qdrant_path": self._qdrant_path if not self._qdrant_url else None,
            "qdrant_url": self._qdrant_url,
            "docs_dir": self._docs_dir,
            "embedding_model": self._embedding_model,
        }
