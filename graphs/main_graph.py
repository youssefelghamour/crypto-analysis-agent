
"""Main LangGraph workflow orchestrating discussion and report requests."""

import sqlite3

from langchain_core.messages import AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END

from agents.planner import planner_node
from graphs.state import AnalysisState
from graphs.discussion import build_discussion_graph


def build_main_graph():
    """Build the main workflow and configure persistent conversation memory."""

    discussion_graph = build_discussion_graph()

    def discussion_node(state: AnalysisState) -> dict:
        """Run the discussion subgraph using the stored conversation history."""

        result = discussion_graph.invoke({
            "messages": state["messages"]
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

    def report_placeholder(state: AnalysisState) -> dict:
        """Handle report requests temporarily until the report workflow is implemented"""

        return {
            "status": "failed",
            "validation_error": (
                "The report workflow has not been implemented yet."
            ),
        }

    def route_request(state: AnalysisState) -> str:
        """Select the workflow based on the planner's decision"""

        return state["intent"]


    # Build the main graph
    graph_builder = StateGraph(AnalysisState)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("discussion", discussion_node)
    graph_builder.add_node("report", report_placeholder)

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
