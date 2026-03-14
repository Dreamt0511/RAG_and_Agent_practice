"""
https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs#multiple-agent-subgraphs
"""
import logging
from typing import Literal
from langchain.agents import AgentState, create_agent
from langchain.messages import AIMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing_extensions import NotRequired
from langchain_community.chat_models.tongyi import ChatTongyi


# ✅ 必须配置 basicConfig，否则不会显示
logging.basicConfig(level=logging.INFO)

# 1. Define state with active_agent tracker
class MultiAgentState(AgentState):
    active_agent: NotRequired[str]#NotRequired：用于 TypedDict，表示键可选，但值类型不变


# 2. Create handoff tools
@tool(description="转换到销售agent")
def transfer_to_sales(
    runtime: ToolRuntime,
) -> Command:
    last_ai_message = next(msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage))
    """
    等价的使用循环（冗长）
    last_ai_message = None
for msg in reversed(messages):
    if isinstance(msg, AIMessage):
        last_ai_message = msg
        break  # 找到后立即退出循环
    """
    transfer_message = ToolMessage(
        content="Transferred to sales agent from support agent",
        tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto="sales_agent",
        update={
            "active_agent": "sales_agent",
            "messages": [last_ai_message, transfer_message],
        },
        graph=Command.PARENT,#在父图级别执行跳转,graph 默认是当前图,这样只会在子图内部查找 "sales_agent" 节点,但 "sales_agent" 可能定义在父图中，导致找不到节点
    )


#主要是更新active_agent为support_agent，这样在route_after+agent的时候就能跳转到support节点
@tool(description="转换到技术支持agent")
def transfer_to_support(
    runtime: ToolRuntime,
) -> Command:
    last_ai_message = next(msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage))
    transfer_message = ToolMessage(
        content="Transferred to support agent from sales agent",
        tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto="support_agent",
        update={
            "active_agent": "support_agent",
            "messages": [last_ai_message, transfer_message],
        },
        graph=Command.PARENT,
    )

model = ChatTongyi(model="qwen-plus")

# 3. Create agents with handoff tools
sales_agent = create_agent(
    model=model,
    tools=[transfer_to_support],
    system_prompt="You are a sales agent. Help with sales inquiries. If asked about technical issues or support, transfer to the support agent.",
)

support_agent = create_agent(
    model=model,
    tools=[transfer_to_sales],
    system_prompt="You are a support agent. Help with technical issues. If asked about pricing or purchasing, transfer to the sales agent.",
)


# 4. Create agent nodes that invoke the agents
def call_sales_agent(state: MultiAgentState) -> Command:
    """Node that calls the sales agent."""
    response = sales_agent.invoke(state)
    logging.info(f"call_sales_agent返回的response为\n{response}")
    return response


def call_support_agent(state: MultiAgentState) -> Command:
    """Node that calls the support agent."""
    response = support_agent.invoke(state)
    logging.info(f"call_support_agent返回的response为{response}")
    return response


# 5. Create router that checks if we should end or continue
def route_after_agent(
    state: MultiAgentState,
) -> Literal["sales_agent", "support_agent", "__end__"]:
    """Route based on active_agent, or END if the agent finished without handoff."""
    messages = state.get("messages", [])

    # Check the last message - if it's an AIMessage without tool calls, we're done
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
            return "__end__"

    # Otherwise route to the active agent
    active = state.get("active_agent", "sales_agent")
    return active if active else "sales_agent"


def route_initial(
    state: MultiAgentState,
) -> Literal["sales_agent", "support_agent"]:
    print(f"初始化的state为\n{state}")
    """Route to the active agent based on state, default to sales agent."""
    return state.get("active_agent") or "sales_agent"
    #初始的state为{'messages': [HumanMessage(content="Hi, I'm having trouble with my account login. Can you help?", additional_kwargs={}, response_metadata={}, id='d9768d3f-fc9f-4d77-9704-5575fdd1b4d0')]}
    #显然没有active_agent，因此一开始会返回"sales_agent"接待客户

# 6. Build the graph
builder = StateGraph(MultiAgentState)
builder.add_node("sales_agent", call_sales_agent)
builder.add_node("support_agent", call_support_agent)

# Start with conditional routing based on initial active_agent
builder.add_conditional_edges(START, route_initial, ["sales_agent", "support_agent"])

# After each agent, check if we should end or route to another agent
builder.add_conditional_edges(
    "sales_agent", route_after_agent, ["sales_agent", "support_agent", END]
)
builder.add_conditional_edges(
    "support_agent", route_after_agent, ["sales_agent", "support_agent", END]
)

graph = builder.compile()
result = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Hi, I'm having trouble with my account login. Can you help?",
            }
        ]
    }
)

for msg in result["messages"]:
    msg.pretty_print()


"""执行流程如下：
# LangGraph 内部自动执行：
1. 接收输入状态
2. 自动调用 route_initial 决定第一个节点
3. 自动进入 sales_agent 节点
4. 自动执行 sales_agent.invoke()  (invoke这里大模型会触发工具调用，工具调用里就是下一步的返回Command)
5. 自动检测返回的 Command()        (Command里会更新参数，参数包括：要跳转的节点，跳转的层级（一般是父节点），要激活的agent和更新的messages)
6. 自动解析 goto 和 graph 参数
7. 自动跳转到 support_agent 节点
8. 自动执行 support_agent.invoke()
9. 自动调用 route_after_agent
10. 自动检测到应该结束
11. 自动返回最终状态


"""