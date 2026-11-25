"""LangGraph subgraph handling the report workflow"""
from langgraph.graph import StateGraph, START, END
from agents.metrics import metrics_node
from agents.analyst import analyst_node
from agents.report_builder import report_builder_node
from graphs.research import build_research_graph
from graphs.state import AnalysisState


def build_report_graph():
    """Builds the report workflow using the shared AnalysisState"""

    research_graph = build_research_graph()

    graph_builder = StateGraph(AnalysisState)

    graph_builder.add_node("research", research_graph)
    graph_builder.add_node("metrics", metrics_node)
    graph_builder.add_node("analyst", analyst_node)
    graph_builder.add_node("report_builder", report_builder_node)

    graph_builder.add_edge(START, "research")
    graph_builder.add_edge("research", "metrics")
    graph_builder.add_edge("metrics", "analyst")
    graph_builder.add_edge("analyst", "report_builder")
    graph_builder.add_edge("report_builder", END)

    return graph_builder.compile()
