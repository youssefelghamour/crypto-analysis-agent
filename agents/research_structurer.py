
"""LLM node responsible for structuring collected research result from the research agent"""

from langchain_core.messages import SystemMessage

from config import llm
from schemas.research import ResearchData


STRUCTURING_PROMPT = """
You convert the Research Agent's messages and tool results into
a ResearchData object.

Rules:
- Extract the cryptocurrency identity and requested analysis period.
- Preserve the market, historical, and news data returned by the tools.
- Never invent or estimate missing values.
- Record coin identification failures in validation_error.
- Record market data failures in market_error.
- Record historical data failures in historical_error.
- Record news failures in news_error.
- Leave unavailable data fields empty or None as appropriate.
"""


structured_llm = llm.with_structured_output(ResearchData)


def research_structurer_node(state: dict) -> dict:
    """Converts collected tool results into validated research data"""

    research_data = structured_llm.invoke(
        [
            SystemMessage(content=STRUCTURING_PROMPT),
            *state["messages"],
        ]
    )

    return {"research_data": research_data}
