"""RAG knowledge-base search tool — LangChain tool wrapping the RAG retriever.

This tool is used by the ``rag_qa`` sub-agent to retrieve relevant documents
from the knowledge base before generating an answer.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import List, Dict, Any, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SearchKnowledgeBaseInput(BaseModel):
    """Input schema for the knowledge base search tool."""

    query: str = Field(
        ...,
        description="搜索查询语句，用中文自然语言描述你想查找的内容。",
    )
    top_k: int = Field(
        default=5,
        description="返回的文档片段数量，默认 5。",
    )


class SearchKnowledgeBaseTool(BaseTool):
    """Search the project knowledge base for relevant documents.

    Returns the top-k most relevant document chunks with their source metadata.
    The rag_qa agent uses these chunks as context for generating answers.
    """

    name: str = "search_knowledge_base"
    description: str = (
        "搜索项目知识库，获取与查询相关的文档片段。"
        "返回格式：{\"results\": [{\"content\": \"文档内容...\", \"source\": \"文件名\", \"score\": 0.92}, ...], \"total\": 5}\n"
        "- query: 搜索查询语句，中文自然语言描述\n"
        "- top_k: 返回片段数量（默认 5）\n"
        "- results 按相关度从高到低排序\n"
        "- score 越高表示越相关\n"
        "- 当知识库为空时返回空列表"
    )
    args_schema: Type[BaseModel] = SearchKnowledgeBaseInput

    def _run(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Synchronous search."""
        from src.rag import get_rag_retriever

        retriever = get_rag_retriever()
        try:
            docs = retriever.search(query, top_k=top_k)
        except Exception as exc:
            logger.error("Knowledge base search failed: %s", exc)
            return {"results": [], "total": 0, "error": str(exc)}

        results = []
        for doc in docs:
            source = doc.metadata.get("source", "未知来源")
            results.append({
                "content": doc.content,
                "source": source,
                "score": round(doc.score, 4),
            })

        return {
            "results": results,
            "total": len(results),
        }

    async def _arun(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Async search."""
        from src.rag import get_rag_retriever

        retriever = get_rag_retriever()
        try:
            docs = await retriever.asearch(query, top_k=top_k)
        except Exception as exc:
            logger.error("Knowledge base search failed: %s", exc)
            return {"results": [], "total": 0, "error": str(exc)}

        results = []
        for doc in docs:
            source = doc.metadata.get("source", "未知来源")
            results.append({
                "content": doc.content,
                "source": source,
                "score": round(doc.score, 4),
            })

        return {
            "results": results,
            "total": len(results),
        }


# ── Singleton instance ───────────────────────────────────────────────────────
search_knowledge_base_tool = SearchKnowledgeBaseTool()
