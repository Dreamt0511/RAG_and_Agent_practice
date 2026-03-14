from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from typing import Callable, Optional
from langchain_community.chat_models.tongyi import ChatTongyi

# 定义状态跟踪，方便判断使用什么身份
class SupportState(AgentState):
    current_step: str
    warranty_status: Optional[str]

# 在工具中通过Command更新current_step
@tool(description="记录保险单的状态然后跳转到对应步骤")
def record_warranty_status(
        status: str,
        runtime: ToolRuntime[None, SupportState]
) -> Command:
    print(f"在工具中打印保单状态{status}")
    if status == "in_warranty":
        current_step = "specialist"
        message = f"保单状态{status},为您转接到专家售后服务"
    else:
        current_step = "triage"  # 转到计费或澄清环节
        message = f"Warranty status recorded: {status}. Let's discuss your options."

    # 更新相关配置
    return Command(update={
        "messages": [ToolMessage(content=message, tool_call_id=runtime.tool_call_id)],
        "warranty_status": status,
        "current_step": current_step
    })

@tool(description="提供解决策略")
def provide_solution():
    pass

@tool(description="升级权限")
def escalate():
    pass

# 3. Middleware applies dynamic configuration based on current_step
@wrap_model_call()
def apply_step_config(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Configure agent behavior based on current_step."""
    step = request.state.get("current_step", "triage")

    configs = {
        "triage": {
            "prompt": "你是一个售后支持助手。请收集用户的保修信息。如果用户提到保修状态，使用record_warranty_status工具记录。",
            "tools": [record_warranty_status]
        },
        "specialist": {
            "prompt": f"你是一个专家支持助手。当前用户保修状态为: {request.state.get('warranty_status', '未知')}。请根据保修状态提供解决方案。",
            "tools": [provide_solution, escalate]
        }
    }

    config = configs.get(step, configs["triage"])

    # 修复：直接使用字符串，不需要格式化
    request = request.override(
        system_message=SystemMessage(config["prompt"]),
        tools=config["tools"]
    )

    return handler(request)

model = ChatTongyi(
    model="qwen-plus"
)

agent = create_agent(
    model=model,
    state_schema=SupportState,
    tools=[escalate, provide_solution, record_warranty_status],
    middleware=[apply_step_config],
    checkpointer=InMemorySaver()  # Persist state across turns
)

checkpoint_config = {"configurable": {"thread_id": "1"}}

# 第一轮对话
res = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "我的手机坏了，但在保质期内，该怎么办"}
        ]
    },
    checkpoint_config
)

print("第一轮回复:", res["messages"][-1].content)

# 第二轮对话（模拟用户提供保修状态）
res2 = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "保修期到2024年"}
        ]
    },
    checkpoint_config
)

print("第二轮回复:", res2["messages"][-1].content)

# 第三轮对话（此时状态应该已变为specialist）
res3 = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "具体怎么修？"}
        ]
    },
    checkpoint_config
)

print("第三轮回复:", res3["messages"][-1].content)

"""
https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs
A single agent changes its behavior based on state.
Middleware intercepts each model call and dynamically adjusts the system prompt and available tools.
Tools update the state variable to trigger transitions:

通过state结合中间件实现动态agent交接，下面是一个售后支持的实现方式
# 多轮对话示例
第一轮：用户说 "我的手机坏了"
    → 状态：current_step = "triage" (已保存)

第二轮：AI问 "保修期到什么时候？"
    用户说 "到2024年"
    → AI记录保修状态，更新 current_step = "specialist" (自动保存)

第三轮：用户问 "怎么修？"
    → 系统读取状态：warranty_status="in_warranty", current_step="specialist"
    → 直接进入 specialist 模式提供保修期内解决方案
"""

