
"""LLM node responsible for collecting cryptocurrency research using the provided tools"""
from langchain_core.messages import SystemMessage
from langchain_core.messages.utils import count_tokens_approximately
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
- Each research tool should normally be called only once per request.
- After receiving a successful result from a tool, reuse that result.
  Do not call the same tool again for the same cryptocurrency and analysis period.
- Repeated calls to the same tool with identical arguments will not provide new information.
- Only retry a tool if its previous call failed or returned incomplete data
  that can reasonably be corrected with different arguments.
- Once you have successfully collected cryptocurrency identity, current market data,
  historical data, and recent news, stop calling tools and provide your final response.

- IMPORTANT: crypto_history_tool returns a short confirmation because its full
result is saved directly in the workflow state for downstream nodes.
A successful confirmation means the historical data has been retrieved.
Never call crypto_history_tool again to obtain or inspect that data.
Do not mistake the short confirmation for missing historical data.
"""


llm_with_tools = llm.bind_tools(tools)


def research_agent_node(state: dict) -> dict:
   """Select the next research tool or finish evidence collection"""
   
   for i, message in enumerate(state["messages"]):
      print(
         f"Message {i}: {type(message).__name__} | "
         f"Tool: {getattr(message, 'name', None)} | "
         f"{count_tokens_approximately([message])} tokens"
      )

   response = llm_with_tools.invoke(
      [
         SystemMessage(content=RESEARCH_PROMPT),
         *state["messages"],
      ]
   )

   return {"messages": [response]}
