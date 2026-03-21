from langgraph.graph import StateGraph
from typing import TypedDict

class State(TypedDict):
    question: str

graph = StateGraph(State)

graph.add_sequence()
