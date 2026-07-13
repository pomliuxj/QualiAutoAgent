"""Main orchestrator graph — intent recognition → router → sub-agent → END.

Sub-agents are added as **nested compiled graphs** (not wrapper functions).
This means ``astream_events`` automatically emits sub-agent internal node
events with proper namespacing, giving full visibility into each step.

Topology::

    START
      │
      ▼
    intent_recognition
      │
      ├──(general_chat)──► general_response ──► END
      │
      └──(matched sub-agent)
            │
            ▼
          <sub-agent graph>  ← nested compiled StateGraph
            │                   (events streamed transparently)
            ▼
          END
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field, field_validator

from src.framework.registry import get as get_sub_agent, list_all as list_sub_agents

logger = logging.getLogger(__name__)


# ── Intent classification model ────────────────────────────────────────────
class IntentClassification(BaseModel):
    """LLM structured output for intent recognition."""

    intent: str = Field(
        description="Intent type: 'test_case_generation', 'scenario_test_generation', "
        "'code_quality_analysis', 'knowledge_qa', or 'general_chat'",
    )
    agent_id: str = Field(
        default="",
        description="Matched sub-agent id from the registry, or empty for general_chat",
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence score as a number between 0.0 and 1.0 (e.g. 0.95 for high confidence)",
    )
    reasoning: str = Field(default="", description="Brief reasoning for the classification")

    @field_validator("confidence", mode="before")
    @classmethod
    def coerce_confidence(cls, v):
        """Accept string labels (high/medium/low) in addition to numeric values."""
        if isinstance(v, str):
            mapping = {"high": 0.95, "medium": 0.7, "low": 0.4}
            return mapping.get(v.lower().strip(), 0.5)
        return v


# ── Node: intent_recognition ───────────────────────────────────────────────
async def _intent_recognition(state: dict) -> Command:
    """Classify user intent and route to sub-agent or general chat.

    Two-tier strategy:
    1. Keyword pre-filter from registry (fast path)
    2. LLM classification (handles ambiguous / nuanced inputs)
    """
    messages = state.get("messages", [])
    if not messages:
        return Command(goto=END)

    last = messages[-1]
    user_input = last.content if hasattr(last, "content") else str(last)

    # Tier 1 — keyword match
    from src.framework.registry import match_by_keywords
    keyword_match = match_by_keywords(user_input)

    # Tier 2 — LLM classification
    from src.llms.llm import get_llm_by_type
    from src.config.agents import AGENT_LLM_MAP

    llm = get_llm_by_type(AGENT_LLM_MAP.get("basic", "basic"))

    available = list_sub_agents()
    agent_list = "\n".join(
        f"- {a.agent_id}: {a.name} — {a.description}"
        for a in available.values()
    ) if available else "- (no sub-agents registered)"

    from src.prompts.templates import PROMPT_TEMPLATES
    template = PROMPT_TEMPLATES.get("intent_recognition", {}).get("system", "")
    prompt = template.format(agent_list=agent_list, user_input=user_input)

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        text = response.content
        # Extract JSON from markdown code block or raw text
        match = re.search(r"\{[^{}]*\"intent\"[^{}]*\}", text, re.DOTALL)
        if not match:
            match = re.search(r"\{.*\}", text, re.DOTALL)
        json_str = match.group(0) if match else text
        data = json.loads(json_str)
        result = IntentClassification(**data)
        logger.info(
            "Intent: %s (agent=%s, confidence=%.2f)",
            result.intent, result.agent_id, result.confidence,
        )
        intent = result.intent
        agent_id = result.agent_id
    except Exception as exc:
        logger.error("Intent recognition failed: %s", exc)
        intent = "general_chat"
        agent_id = ""

    # Validate agent_id exists in registry
    if agent_id and not get_sub_agent(agent_id):
        logger.warning("Unknown agent_id='%s', falling back", agent_id)
        agent_id = ""

    # Keyword fallback when LLM didn't pick an agent
    if not agent_id and keyword_match:
        agent_id = keyword_match
        logger.info("Keyword fallback → agent_id='%s'", agent_id)

    # Resolve display name for status message
    sub_def = get_sub_agent(agent_id) if agent_id else None
    sub_name = sub_def.name if sub_def else agent_id

    update: dict = {
        "messages": [
            AIMessage(
                content=(
                    f"进入子智能体「{sub_name}」" if agent_id
                    else f"意图识别结果：{intent}"
                ),
                name="intent_recognition",
            )
        ],
        "intent_type": intent,
        "intent_agent_id": agent_id,
    }

    if intent != "general_chat" and agent_id:
        return Command(update=update, goto=agent_id)

    return Command(update=update, goto="general_response")


# ── Node: general_response ─────────────────────────────────────────────────
async def _general_response(state: dict) -> Command:
    """Knowledge Q&A for general questions."""
    messages = state.get("messages", [])
    user_input = ""
    if messages:
        last = messages[-1]
        user_input = last.content if hasattr(last, "content") else str(last)

    from src.llms.llm import get_llm_by_type
    from src.config.agents import AGENT_LLM_MAP

    llm = get_llm_by_type(AGENT_LLM_MAP.get("basic", "basic"))

    prompt = f"""你是一个 API 自动化测试平台的智能助手。请用中文简洁回答用户问题。

平台支持的功能：
- API 接口测试用例自动生成（单接口 + 多接口业务场景）
- 自动化测试执行与断言校验
- Swagger/OpenAPI 接口文档导入
- 全局变量与数据驱动测试
- 代码质量分析
- 定时任务与测试报告

用户问题：{user_input}"""

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        reply = response.content
    except Exception:
        reply = "抱歉，暂时无法处理您的问题，请稍后重试。"

    return Command(
        update={
            "messages": [AIMessage(content=reply, name="general_response")],
        },
        goto=END,
    )


# ── Build orchestrator ─────────────────────────────────────────────────────
def build_orchestrator_graph(
    sub_agent_ids: Optional[list[str]] = None,
    checkpointer=None,
) -> StateGraph:
    """Build the compiled orchestrator graph.

    Sub-agents are added as **nested compiled graphs** — LangGraph streams
    their internal node events transparently through ``astream_events``,
    giving full visibility into every step of every sub-agent.

    Parameters:
        sub_agent_ids: Subset of sub-agent IDs (default: all registered).
        checkpointer:  Checkpoint saver (default: framework SqliteSaver / InMemorySaver).
    """

    if sub_agent_ids is None:
        sub_agent_ids = list(list_sub_agents().keys())

    builder = StateGraph(dict)

    # ── Core orchestrator nodes ─────────────────────────────────────────
    builder.add_node("intent_recognition", _intent_recognition)
    builder.add_node("general_response", _general_response)

    # ── Sub-agents as nested compiled graphs ────────────────────────────
    for agent_id in sub_agent_ids:
        defn = get_sub_agent(agent_id)
        if defn is None:
            logger.warning("Skipping unknown sub-agent '%s'", agent_id)
            continue
        # Adding a compiled StateGraph as a node makes it a nested subgraph.
        # LangGraph handles state passing, event streaming, and interrupt
        # propagation transparently.
        builder.add_node(agent_id, defn.graph)
        logger.info(
            "Orchestrator: registered sub-agent '%s' (%s) as nested graph",
            agent_id, defn.name,
        )

    # ── Static edges ────────────────────────────────────────────────────
    builder.add_edge(START, "intent_recognition")
    builder.add_edge("general_response", END)
    # Each sub-agent exits directly to END after completing its internal flow
    for agent_id in sub_agent_ids:
        if agent_id in builder.nodes:
            builder.add_edge(agent_id, END)

    return builder.compile(checkpointer=checkpointer)


# ── Node label mapping for streaming ───────────────────────────────────────
# Extended by ``get_node_labels()`` which adds sub-agent internal node labels.
_BASE_NODE_LABELS = {
    "intent_recognition": "意图识别",
    "general_response": "智能回答",
}


def get_node_labels() -> dict[str, str]:
    """Return the full node-label mapping including all sub-agent nodes.

    Called by ``stream_main()`` to resolve Chinese display names for every
    node in the graph (orchestrator + sub-agents).
    """
    labels = dict(_BASE_NODE_LABELS)
    # Merge sub-agent internal node labels
    for agent_id, defn in list_sub_agents().items():
        # Sub-agent name as the entry label
        labels[agent_id] = defn.name
        # Each sub-agent can export its own node labels
        if hasattr(defn, "node_labels") and defn.node_labels:
            labels.update(defn.node_labels)
    return labels
