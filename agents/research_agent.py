
"""LLM node responsible for collecting cryptocurrency research using the provided tools"""
from langchain_core.messages import SystemMessage

from config import llm
from tools import tools


RESEARCH_PROMPT = """
You are a cryptocurrency research agent.

Your task is to collect evidence for a cryptocurrency market report.

Follow these steps:

1. Identify the requested cryptocurrency.
   - Use crypto_search_tool to find its CoinGecko ID.
   - Verify its name and symbol to avoid selecting the wrong coin.
   - If the identity is ambiguous, do not guess.

2. Retrieve current market data using crypto_data_tool.

3. Retrieve historical price and volume data using crypto_history_tool.
   - Use the requested analysis period.
   - Supported periods are 1, 7, 14, and 30 days.

4. Retrieve recent news using crypto_news_tool.
   - Search using the identified cryptocurrency's name.

Rules:
- Use tools to collect data. Never invent market information or news.
- Do not calculate additional metrics.
- If one tool fails, continue with the remaining research tasks.
- Do not confuse missing data with a confirmed negative result.
"""


llm_with_tools = llm.bind_tools(tools)


def research_agent_node(state: dict) -> dict:
    """Select the next research tool or finish evidence collection."""

    response = llm_with_tools.invoke(
        [
            SystemMessage(content=RESEARCH_PROMPT),
            *state["messages"],
        ]
    )

    return {"messages": [response]}
