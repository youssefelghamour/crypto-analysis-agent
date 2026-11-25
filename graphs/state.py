"""LangGraph state"""
from typing import TypedDict, Literal, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from schemas import MarketReport, ResearchData



class AnalysisState(TypedDict):
    # Original request from the user
    request: str

    intent: Literal["discussion", "report"]
    routing_reason: str

    # Research target cryptocurrency info
    coin_id: str | None
    coin_name: str | None
    coin_symbol: str | None
    period_days: int | None

    # Discussion branch output
    discussion_response: str | None

    # Conversation history, preserved across turns
    messages: Annotated[list[AnyMessage], add_messages]

    # Output of the research agent
    research_data: ResearchData | None

    # Raw data returned by the research tools
    market_data: dict | None
    historical_data: dict | None
    news_data: list[dict]

    # Research errors
    validation_error: str | None
    market_error: str | None
    historical_error: str | None
    news_error: str | None

    # Calculated market metrics (Python calculations)
    metrics: dict | None

    # Structured outputs from the analyst
    analysis: dict | None
    critique: dict | None
    # Tracks how many times the analyst has revised its analysis
    revision_count: int

    # Final validated report
    final_report: MarketReport | None

    # Current workflow status
    status: Literal[
        "pending",
        "discussing",
        "researching",
        "analyzing",
        "reviewing",
        "completed",
        "failed",
    ]
