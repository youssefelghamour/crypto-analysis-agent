"""LangGraph subgraph for cryptocurrency research

The Research Agent identifies the requested cryptocurrency and gets
current market data, historical data, and recent news using the provided tools

The structuring Agent structures the LLM response from the Research Agent into research_data in the state
"""

import json
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from agents.research_agent import research_agent_node
from agents.research_structurer import research_structurer_node
from graphs.state import AnalysisState
from tools import tools



def build_research_graph():
    """Build the research subgraph using the shared AnalysisState"""

    def execute_research_tools(state: AnalysisState) -> dict:
        """Tool node wrapper that executes research tools and keep large historical
            results outside message history to avoid exceeding the rate limit

            Saves full historical results in the state while replacing ToolMessage with a short msg
            The structurer's LLM message won't include the historical_data in this case
        """

        result = ToolNode(tools).invoke(state)

        messages = result["messages"]

        for message in messages:
            if message.name == "crypto_history_tool":
                historical_data = json.loads(message.content)

                return {
                    "messages": [
                        ToolMessage(
                            content="Historical data retrieved successfully.",
                            tool_call_id=message.tool_call_id,
                            name=message.name,
                        )
                    ],
                    "historical_data": historical_data,  # Saves it directly to the state, before the structurer
                }

        return {"messages": messages}
    

    def route_after_agent(state: AnalysisState) -> str:
        """Execute requested tools or proceed to structured output agents"""

        last_message = state["messages"][-1]

        if last_message.tool_calls:
            return "tools"

        return "structurer"
    

    def map_research_data(state: dict) -> dict:
        """Map the structured research output into AnalysisState fields"""

        research_data = state["research_data"]

        # "historical_data": research_data.historical_data is removed because the LLM doesn't receive it
        # Normally we wait for the structurer to fill those fields in the state,
        # but now our tool node saves this field directly to the state before the structurer
        return {
            "coin_id": research_data.coin_id,
            "coin_name": research_data.coin_name,
            "coin_symbol": research_data.coin_symbol,
            "period_days": research_data.period_days,
            "market_data": research_data.market_data,
            "news_data": research_data.news_data,
            "validation_error": research_data.validation_error,
            "market_error": research_data.market_error,
            "historical_error": research_data.historical_error,
            "news_error": research_data.news_error,
        }


    graph_builder = StateGraph(AnalysisState)

    graph_builder.add_node("research_agent", research_agent_node)
    graph_builder.add_node("tools", execute_research_tools)
    graph_builder.add_node("structurer", research_structurer_node)
    graph_builder.add_node("map_research_data", map_research_data)

    graph_builder.add_edge(START, "research_agent")

    graph_builder.add_conditional_edges(
        "research_agent",
        route_after_agent,
        {
            "tools": "tools",
            "structurer": "structurer",
        },
    )

    graph_builder.add_edge("tools", "research_agent")
    graph_builder.add_edge("structurer", "map_research_data")
    graph_builder.add_edge("map_research_data", END)

    return graph_builder.compile()
