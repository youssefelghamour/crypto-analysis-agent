import sqlite3

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from config import llm
from tools import tools
from .prompts import SYSTEM_PROMPT


def build_graph():
    """Build and compile the existing tool-calling conversation graph"""
    tool_node = ToolNode(tools)
    llm_with_tools = llm.bind_tools(tools)

    def assistant(state: MessagesState):
        """
        Receives the current conversation and sends it to the LLM
        """
        # Include the system message before the conversation messages
        system_message = SystemMessage(content=SYSTEM_PROMPT)

        # Inboke the LLM with access to the tools
        response = llm_with_tools.invoke(
            [system_message] + state['messages']
        )

        return {"messages": [response]}

    # Create the graph using MessagesState to manage conversation messages
    graph_builder = StateGraph(MessagesState)

    # Register the nodes
    graph_builder.add_node("assistant", assistant)
    graph_builder.add_node("tools", tool_node)

    # Connect the nodes
    graph_builder.add_edge(START, "assistant")

    # Route to tools if the assistant requests them, otherwise end
    graph_builder.add_conditional_edges("assistant", tools_condition)

    # After executing tools, return to the assistant
    graph_builder.add_edge("tools", "assistant")

    # SQLite conversation checkpoint.
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=memory)

    return graph, conn
