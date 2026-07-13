# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server.controller import chat_controller

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Test Case Generation API",
    description="API for AI-driven automated test case generation",
    version="0.1.0",
)

# CORS middleware — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat_controller.router)


@app.on_event("startup")
async def startup():
    """Register sub-agents and pre-warm RAG knowledge base on startup."""
    try:
        import src.agents  # noqa: F401 — triggers sub-agent self-registration
        from src.framework.registry import list_all
        agents = list_all()
        logger.info("Sub-agents registered: %s", list(agents.keys()))
    except Exception as exc:
        logger.error("Failed to register sub-agents: %s", exc)

    # Pre-warm RAG: index documents on startup so first query is fast
    try:
        from src.rag import get_rag_retriever
        retriever = get_rag_retriever()
        stats = retriever.get_stats()
        logger.info("RAG pre-warmed: %s", stats)
    except Exception as exc:
        logger.warning("RAG pre-warm skipped: %s", exc)
