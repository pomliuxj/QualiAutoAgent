"""RAG QA (Retrieval-Augmented Generation Q&A) — knowledge-base intelligent agent.

Graph topology::

    START
      │
      ▼
    rag_qa_agent  — ReAct agent with search_knowledge_base tool
      │              LLM decides when to search, how to answer, and cites sources
      ▼
    END

The ReAct agent uses ``search_knowledge_base`` to retrieve relevant documents,
then generates a comprehensive answer with citations.
"""

from __future__ import annotations

import logging

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_core.messages import AIMessage

from src.framework import register_sub_agent, SubAgentDefinition
from src.agents.agents import create_agent
from src.shared.rag_tools import search_knowledge_base_tool

logger = logging.getLogger(__name__)


# ── Node: ReAct agent ────────────────────────────────────────────────────────

async def _rag_qa_agent(state: dict) -> Command:
    """ReAct agent — searches knowledge base then answers with citations."""
    agent = await create_agent(
        agent_type="rag_qa",
        agent_name="rag_qa_agent",
        prompt_template="rag_qa",
        tools=[search_knowledge_base_tool],
    )
    result = await agent.ainvoke(state)
    last_msg = result.get("messages", [None])[-1] if result.get("messages") else None
    content = last_msg.content if last_msg and hasattr(last_msg, "content") else "抱歉，无法处理您的问题。"

    return Command(
        update={
            "messages": [AIMessage(content=content, name="rag_qa_agent")],
        },
        goto=END,
    )


# ── Build ────────────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Build the compiled RAG QA graph (single ReAct node)."""
    builder = StateGraph(dict)

    builder.add_node("rag_qa_agent", _rag_qa_agent)

    builder.add_edge(START, "rag_qa_agent")
    builder.add_edge("rag_qa_agent", END)

    return builder.compile()


# ── Register ─────────────────────────────────────────────────────────────────

def register():
    """Register this sub-agent with the framework."""
    register_sub_agent(
        SubAgentDefinition(
            agent_id="rag_qa",
            name="知识库问答",
            description="基于项目知识库的智能问答，检索文档后生成精准回答，支持引用来源",
            graph=build_graph(),
            intent_keywords=[
                "文档", "帮助", "怎么", "如何", "说明",
                "指南", "知识库", "介绍", "FAQ", "常见问题",
                "什么是", "怎么做", "教程", "使用说明", "功能",
                "操作指南", "步骤", "配置", "部署", "安装",
                "help", "how to", "guide", "documentation",
                "what is", "tutorial", "manual",
            ],
            icon="el-icon-reading",
            node_labels={
                "rag_qa_agent": "知识库检索问答",
            },
        )
    )
    logger.info("RagQAAgent registered")


# Auto-register on import
register()
