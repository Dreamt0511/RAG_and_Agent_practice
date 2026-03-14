"""
通过在消息上下文中注入存储的用户风格让agent写邮件
参考链接
https://docs.langchain.com/oss/python/langchain/context-engineering#store-2
Messages make up the prompt that is sent to the LLM.
It’s critical to manage the content of messages to ensure that the LLM has the right information to respond well.
"""
import os
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable
from langgraph.store.memory import InMemoryStore
from langchain_community.chat_models.tongyi import ChatTongyi

"""这里先在内存中存入用户的写作风格"""
# 存储到 store 中的数据格式
writing_style_data = {
    "tone": "严厉",
    "greeting": "你好",
    "sign_off": "祝好",
    "example_email": ""
}
store = InMemoryStore()
# 存储到 store
store.put(("writing_style",), "user123", writing_style_data)


@dataclass
class Context:
    user_id: str


@wrap_model_call
def inject_writing_style(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Inject user's email writing style from Store."""
    user_id = request.runtime.context.user_id

    store = request.runtime.store  # 这个store也可以是从数据库中读取的关于用户的长期记忆信息
    writing_style = store.get(("writing_style",), user_id)

    if writing_style:
        style = writing_style.value
        style_context = f""""你的写作风格是：
        语调：{style.get("tone", "professional")}
        开头：{style.get("greeting", "尊敬的...")}
        结尾：{style.get("sign_off", "再见")}
        下面是一篇示例邮件：{style.get("example_email", "")}    
        """
        # 把构造好的消息添加到消息列表结尾
        messages = [
            *request.messages,  # 解包原消息列表
            {"role": "user", "content": style_context}  # 把写作风格追加到结尾
        ]
        # 使用override函数覆盖:用新的消息列表覆盖原来的消息列表
        request = request.override(messages=messages)

        """
        *request.messages 将原来的消息列表解包

然后将新的风格提示作为一条新的用户消息追加到末尾

为什么追加到末尾？利用模型的"近因效应"——模型对最后输入的内容关注度最高

request.override(messages=messages) 创建一个新的请求对象，用修改后的消息列表替换原消息"""

    return handler(request)


model = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

agent = create_agent(
    model=model,
    tools=[],
    middleware=[inject_writing_style],
    context_schema=Context,
    store=store
)

# res = agent.invoke({"messages":"帮我写一份发给弟弟的邮件",},context=Context(user_id="user_123"))
# last_message = res["messages"][-1]
# last_message.pretty_print()

# 流式输出
# 使用 stream 方法替代 invoke
res = agent.stream(
    {"messages": [{"role": "user", "content": "帮我写一份发给弟弟的邮件"}]},
    context=Context(user_id="user123"),
    stream_mode="values"
)

for chunk in res:
    latest_message = chunk["messages"][-1]

    print(latest_message)
    latest_message.pretty_print()

