# 首先安装必要包
# pip install langgraph
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
import os
os.getenv("DASHSCOPE_API_KEY")

# 1. 定义工具
@tool
def get_length(text: str) -> str:
    """返回文本的长度"""
    return str(len(text))

@tool
def add(a: float, b: float) -> float:
    """两个数字相加"""
    return a + b

tools = [get_length, add]

# 2. 初始化千问模型
llm = ChatTongyi(
    model="qwen-plus",
)

# 3. 使用 LangGraph 创建 Agent（这是新版的标准方式）
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个有帮助的助手，可以使用提供的工具回答问题。"
)

# 4. 直接调用 agent（不需要 AgentExecutor）
print("="*50)
print("测试1: 计算文本长度")
result1 = agent.invoke({
    "messages": [HumanMessage(content="计算 'hello world, 千问你好' 这个文本的长度")]
})
print(f"最终答案: {result1['messages'][-1].content}")

print("\n" + "="*50)
print("测试2: 使用加法工具")
result2 = agent.invoke({
    "messages": [HumanMessage(content="计算 123.45 加上 678.90 的结果")]
})
print(f"最终答案: {result2['messages'][-1].content}")