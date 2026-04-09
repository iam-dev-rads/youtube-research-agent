from langgraph.graph import StateGraph, END

from app.agents.nodes import enrich_node, notify_node, search_node, summarise_node
from app.models.agent import AgentState
from app.models.research import ResearchStatus


def should_continue(state: AgentState) -> str:
    if state.result.status == ResearchStatus.FAILED:
        return "end"
    return "continue"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("search", search_node)
    graph.add_node("enrich", enrich_node)
    graph.add_node("summarise", summarise_node)
    graph.add_node("notify", notify_node)

    # Entry point
    graph.set_entry_point("search")

    # Edges with conditional bail-out on failure
    graph.add_conditional_edges(
        "search",
        should_continue,
        {"continue": "enrich", "end": END},
    )
    graph.add_conditional_edges(
        "enrich",
        should_continue,
        {"continue": "summarise", "end": END},
    )
    graph.add_edge("summarise", "notify")
    graph.add_edge("notify", END)

    return graph.compile()


agent = build_graph()