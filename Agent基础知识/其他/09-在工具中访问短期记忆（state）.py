"""

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
from langchain.agents import create_agent
from langchain.tools import tool,ToolRuntime
from langgraph.prebuilt import ToolRuntime


@tool(description="查询用户个人信息")
def get_user_ifo(runtime:ToolRuntime):
    pass

agent = create_agent(
    model="qwen-max",
    tools=[]
)
