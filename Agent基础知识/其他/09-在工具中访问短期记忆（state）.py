"""
参考链接：
https://docs.langchain.com/oss/python/langchain/short-term-memory
一个非常重要的LangChain Agent机制：如何在工具中访问短期记忆（state）。
核心概念图解
# 用户消息
"帮我查一下天气，记得我叫Bob"

         ↓
# Agent流程
┌─────────────────────────────────────┐
│ 1. LLM看到的消息：                    │
│    "帮我查一下天气，记得我叫Bob"       `│
│                                     │
│ 2. LLM决定调用工具：                  │
│    get_weather(city="北京")          │← runtime参数是隐藏的
│                                      │
│ 3. 实际工具调用：                      │
│    get_weather(city="北京", runtime: Runtime) │← runtime自动传入

可以这样访问state:state = runtime.state
    而messages = state["messages"]

核心思想：通过隐藏的 runtime 参数，让工具既能访问完整的Agent状态，又不会增加模型的复杂度。
"""
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime
from langchain_community.chat_models import ChatTongyi


# 自定义状态字段,原有的比如runtime.state["message"]
class CustomState(AgentState):
    user_id: str
    user_name: str
    user_age: int
    user_kg: str


model = ChatTongyi(model="qwen3-max")


@tool(description="查询用户个人信息")
def get_user_ifo(runtime: ToolRuntime):
    #print(runtime.state)
    state = runtime.state
    user_id = state["user_id"]
    if user_id == "111":
        user_name = state["user_name"]
        user_age = state["user_age"]
        user_kg = state["user_kg"]

        return user_kg, user_id, user_name, user_age
    else:
        return "暂未查到您的信息"


agent = create_agent(
    model=model,
    tools=[get_user_ifo],
    state_schema=CustomState,
)
res = agent.invoke({
    "messages": "查询一下我的个人信息",
    "user_id": "111",#这个参数用来在调用工具中判断user_id动态改变工具返回值
    "user_name": "Dreamt",
    "user_age": 25,
    "user_kg": "50kg"
})

last_message = res["messages"][-1].pretty_print()
