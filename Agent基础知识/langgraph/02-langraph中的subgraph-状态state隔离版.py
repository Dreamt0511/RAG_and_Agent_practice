"""
参考链接
https://docs.langchain.com/oss/python/langgraph/use-subgraphs#call-a-subgraph-inside-a-node
类型：子图和主图的状态隔离版本，子图和主图的状态结构不同，需要在它们之间进行状态转换，主图提供invoke调用子图
适用场景
父图和子图有不同的状态结构（没有共享的键）
需要在它们之间进行状态转换
When the parent graph and subgraph have different state schemas (no shared keys), invoke the subgraph inside a node function. 
This is common when you want to keep a private message history for each agent in a multi-agent system.
The node function transforms the parent state to the subgraph state before invoking the subgraph, 
and transforms the results back to the parent state before returning.

The node function transforms the parent state to the subgraph state before invoking the subgraph, 
and transforms the results back to the parent state before returning.


总结成一句话就是：在一个节点当中调用子图
"""
from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph, START

# Define subgraph
class SubgraphState(TypedDict):
    # note that none of these keys are shared with the parent graph state
    bar: str
    baz: str

def subgraph_node_1(state: SubgraphState):
    return {"baz": "baz"}

def subgraph_node_2(state: SubgraphState):
    return {"bar": state["bar"] + state["baz"]}

subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()

# Define parent graph
class ParentState(TypedDict):
    foo: str

def node_1(state: ParentState):
    return {"foo": "hi! " + state["foo"]}

def node_2(state: ParentState):
    # Transform the state to the subgraph state
    response = subgraph.invoke({"bar": state["foo"]})
    # Transform response back to the parent state
    return {"foo": response["bar"]}


builder = StateGraph(ParentState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()

for chunk in graph.stream({"foo": "foo"}, subgraphs=True, version="v2"):
   print(chunk)