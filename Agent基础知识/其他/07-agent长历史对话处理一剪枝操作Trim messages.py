"""
参考链接：https://docs.langchain.com/oss/python/langchain/short-term-memory#trim-messages
Trim messages部分

剪枝实现的机制其实就是 滑动窗口机制，这里通过before_model中间件实现
也可以用after_model实现，不同的是
使用场景
场景	        推荐方式	        原因
节省Token	@before_model	LLM根本看不到旧消息，立即节省token
保持准确性	@after_model	LLM基于完整历史回答，答案更准确
长对话处理	两者结合	        先用完整历史回答，再清理节省存储
"""


from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_core.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime
from typing import Any

model = ChatTongyi(model="qwen3-max")

#定义中间件，对历史消息进行剪枝操作，放置提交的对话历史超过大模型上下文窗口
@before_model
def trim_message(state:AgentState,runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    #默认情况下，agent使用AgentState来管理短期记忆，特别是通过messages键来管理对话历史
    #获取对话历史list
    messages:list = state["messages"]
    #动态裁剪历史消息
    if len(messages) <=3:
        return None#不剪切
    else:#长度超过3保留最近2条消息
        recent_messages  = messages[-2:]
        print("=" * 100)
        print(f"剪枝后的数据为{recent_messages}")
        return {
            "messages":[
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                *recent_messages#解包列表提取元素组成新的消息列表
            ]
        }


agent = create_agent(
    model = model,
    tools= [],
    middleware= [trim_message],
    checkpointer=InMemorySaver(),#采用内存记忆，会随着程序终止而消失，生产环境可以使用数据库读取的checkpoint
)

config = {"configurable":{"thread_id":"001"}}

#写2个invoke是为了展示InMemorySaver的存储功能，从打印的结果可以看出第二次提问时附带上了第一次的对话历史
for i in range(1,5) :#先附带4条消息查看剪枝效果
    agent.invoke({"messages": {"role":"user", "content":"请记住我叫Dreamt"}},config)
#最后一次提问看附带了多少条历史消息
res  =agent.invoke({"messages": {"role":"user", "content":"告诉我我是谁，直接回答"}},config)

print(f"\nAI的最后一次输出为\n")
print(res)

# last_msg = res['messages'][-1]
# last_msg.pretty_print()
