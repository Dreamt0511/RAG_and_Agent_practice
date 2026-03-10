"""
参考链接：https://docs.langchain.com/oss/python/langchain/short-term-memory
"""
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver#适合短期记忆，线程运行过程中记住对话历史
from langgraph.checkpoint.postgres import PostgresSaver #生产环境中，持久化存储，将对话历史保存到PostgreSQL数据库中
from langchain_core.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.store.memory import InMemoryStore


model = ChatTongyi(model = "qwen-plus")

@tool
def get_user_info():
    pass

agent = create_agent(
    model=model,
    tools=[get_user_info],
    checkpointer=InMemorySaver(),
)

agent.invoke(
    {"messages": [{"role": "user", "content": "记住我的名字是"}]},
    {"configurable": {"thread_id": "1"}},
)