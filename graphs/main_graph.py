
"""Main LangGraph workflow orchestrating discussion and report requests."""

import sqlite3
import json

from langchain_core.messages import AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END

from agents.planner import planner_node
from graphs.state import AnalysisState
from graphs.discussion import build_discussion_graph
from graphs.report import build_report_graph


def build_main_graph():
    """Build the main workflow and configure persistent conversation memory."""

    discussion_graph = build_discussion_graph()
    report_graph = build_report_graph()

    def discussion_node(state: AnalysisState) -> dict:
        """Run the discussion subgraph using the stored conversation history."""

        conversation_messages = []

        for message in state["messages"]:
            # Remove/don't include tool messages and assistant tool-call messages
            if message.type == "tool":
                continue

            if isinstance(message, AIMessage) and message.tool_calls:
                continue

            # Remove bulky price and volume history from report messages
            if isinstance(message.content, str):
                content = message.content
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        data.pop("price_history", None)
                        data.pop("volume_history", None)
                        content = json.dumps(data)
                        message = message.model_copy(update={"content": content})
                except (json.JSONDecodeError, TypeError):
                    pass

            conversation_messages.append(message)

        result = discussion_graph.invoke({
            "messages": conversation_messages
        })

        # Extract the final assistant response, excluding tool-call messages
        response = next(
            (
                message
                for message in reversed(result["messages"])
                if isinstance(message, AIMessage) and not message.tool_calls
            ),
            None,
        )

        return {
            "messages": result["messages"],
            "discussion_response": (
                str(response.content) if response else None
            ),
            "status": "completed",
        }
    

    def route_request(state: AnalysisState) -> str:
        """Select the workflow based on the planner's decision"""

        return state["intent"]


    # Build the main graph
    graph_builder = StateGraph(AnalysisState)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("discussion", discussion_node)
    graph_builder.add_node("report", report_graph)

    graph_builder.add_edge(START, "planner")

    graph_builder.add_conditional_edges(
        "planner",
        route_request,
        {
            "discussion": "discussion",
            "report": "report",
        },
    )

    graph_builder.add_edge("discussion", END)
    graph_builder.add_edge("report", END)

    # Conversation persistence
    conn = sqlite3.connect(
        "checkpoints.sqlite",
        check_same_thread=False,
    )
    checkpointer = SqliteSaver(conn)

    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph, conn
