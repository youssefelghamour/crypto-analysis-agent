"""Subgraph for the cryptocurrency conversational assitance"""
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from agents.discussion_agent import discussion_agent_node
from tools import tools



def build_discussion_graph():
    """Build and compile the existing tool-calling conversation graph"""
    tool_node = ToolNode(tools)

    # Create the graph using MessagesState to manage conversation messages
    graph_builder = StateGraph(MessagesState)

    # Register the nodes
    graph_builder.add_node("discussion_agent", discussion_agent_node)
    graph_builder.add_node("tools", tool_node)

    # Connect the nodes
    graph_builder.add_edge(START, "discussion_agent")

    # Route to tools if the discussion_agent requests them, otherwise end
    graph_builder.add_conditional_edges("discussion_agent", tools_condition)

    # After executing tools, return to the discussion_agent
    graph_builder.add_edge("tools", "discussion_agent")

    return graph_builder.compile()
