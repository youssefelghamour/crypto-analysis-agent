
"""Planner node responsible for routing user requests"""
from langchain_core.messages import SystemMessage, HumanMessage

from config import llm
from schemas.routing import RouteDecision


PLANNER_PROMPT = """
You are a request router for a cryptocurrency assistant.

Classify the user's request into one of two categories:

1. discussion:
   - General cryptocurrency questions and explanations.
   - Conversational market discussions.
   - Questions about specific coins or market movements.
   - Comparisons and requests for short answers.

2. report:
   - Explicit requests for a structured market report.
   - Detailed market performance analysis.
   - Requests for a comprehensive report containing metrics,
     historical data, news, and market interpretation.

Rules:
- Current information does not automatically mean a report.
- Mentioning a cryptocurrency does not automatically mean a report.
- When uncertain, choose discussion.
"""


def planner_node(state: dict) -> dict:
    """Classify the user's request and select a workflow."""

    planner = llm.with_structured_output(RouteDecision)

    decision = planner.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=state["request"]),
    ])

    return {
        "intent": decision.intent,
        "routing_reason": decision.reasoning,
    }
