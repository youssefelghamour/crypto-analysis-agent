"""Analyst agent responsible for interpreting cryptocurrency research produced by the research subgraph"""
import json
from langchain_core.messages import SystemMessage, HumanMessage
from config import llm
from schemas.report import MarketAnalysis


ANALYST_PROMPT = """
You are a cryptocurrency market analyst.

Analyze the supplied research evidence and calculated market metrics.

Rules:
- Base every finding on the supplied evidence.
- Do not invent prices, events, statistics, or news.
- Distinguish observed facts from interpretations.
- Explain relevant price movements and market conditions.
- Identify risks supported by the available evidence.
- Provide a cautious outlook, not financial advice.
- If evidence is incomplete or conflicting, acknowledge the limitations.
- Set confidence according to the quality and completeness of the evidence.

Return a structured market analysis.
"""


def analyst_node(state: dict) -> dict:
    """Generate a structured analysis from raw research and calculated metrics."""

    analyst = llm.with_structured_output(MarketAnalysis)

    metrics = state["metrics"]

    evidence = {
        "coin": {
            "id": state["coin_id"],
            "name": state["coin_name"],
            "symbol": state["coin_symbol"],
            "period_days": state["period_days"],
        },
        "market_data": state["market_data"],
        # "historical_data": state["historical_data"],
        "news_data": state["news_data"],
        "metrics": (
            metrics.model_dump()
            if hasattr(metrics, "model_dump")
            else metrics
        ),
        "data_errors": {
            "validation": state["validation_error"],
            "market": state["market_error"],
            "historical": state["historical_error"],
            "news": state["news_error"],
        },
    }

    analysis = analyst.invoke([
        SystemMessage(content=ANALYST_PROMPT),
        HumanMessage(content=json.dumps(evidence, default=str)),
    ])

    return {"analysis": analysis.model_dump()}
