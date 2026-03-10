"""
参考链接：https://docs.langchain.com/oss/python/langchain/short-term-memory
必须在with块内调用：数据库连接只在with块内有效
thread_id保持一致：同一个会话使用相同的thread_id
setup()只需调用一次：表创建后就不需要再调用
跨会话记忆：即使程序重启，只要连接同一个数据库，记忆仍在
[长期记忆使用相同的thread_id]
"""

"""
默认情况：如果不加控制，每次对话都会把全部历史消息都发给AI。随着时间推移，数据会越来越多。如果应用是长期、高频的对话，消息列表会变得非常大。
实际控制：正如官方文档 Short-term memory 中“Customizing agent memory”部分所强调的，长对话会超出模型的上下文窗口。
因此，生产环境中几乎必须采用策略来管理记忆，防止数据爆炸和性能下降：

1.修剪消息 (Trim messages)：只保留最近N条消息，丢弃过时的。

2.删除消息 (Delete messages)：主动移除特定或全部旧消息。

3.总结消息 (Summarize messages)：用AI把旧对话总结成几句话，替代原始的长历史。

这些方法使代理能够跟踪对话而不超出LLM的上下文窗口。
"""
import os

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver#适合短期记忆，线程运行过程中记住对话历史
from langgraph.checkpoint.postgres import PostgresSaver#生产环境中，持久化存储，将对话历史保存到PostgreSQL数据库中
from langchain_core.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi
from contextlib import contextmanager#用于创建上下文管理器

model = ChatTongyi(model = "qwen-plus")

@tool(description= "根据用户id获取用户详细信息的工具")
def get_user_info():
    pass

#读取环境变量中设置的连接地址
DB_URL = os.getenv("user_DB_URL")## 格式: postgresql://用户名:密码@主机:端口/数据库名?

#创建获取agent对象的上下文管理器,这样写的好处是自动获取和释放数据库连接
#传统写法还需checkpoint.close()  # 如果忘了写，可能造成连接泄露
@contextmanager
def get_agent():
    """上下文管理器，自动处理数据库连接"""
    #PostgresSaver.from_conn_string(DB_URL) 创建一个PostgreSQL数据库连接
    #as checkpoint 把连接对象赋值给 checkpoint 变量
    with PostgresSaver.from_conn_string(DB_URL) as checkpoint:
        checkpoint.setup()#自动创建存储对话历史所需的表
        agent = create_agent(
            model = model,
            tools= [get_user_info],
            checkpointer= checkpoint
        )
        yield agent#返回agent供外部使用
        # 退出时自动关闭连接

#使用示例
if __name__ == "__main__":
    #第一次运行，退出with后数据库就自动关闭了
    with get_agent() as agent:
        res = agent.invoke(
            {"messages": [{"role": "user", "content": "请列出我和你的所有对话历史"}]},
            {"configurable": {"thread_id": "user_01"}},
        )

        # 使用pretty_print()输出
        for msg in res["messages"]:
            msg.pretty_print()

