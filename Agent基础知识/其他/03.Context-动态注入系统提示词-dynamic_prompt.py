import datetime
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi

model = ChatTongyi(model = "qwen3-max")

@tool(description="查询当前时间的工具")
def get_current_time() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class ContextSchema:
    user_name: str
    user_age: int

@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name
    user_age = request.runtime.context.user_age
    return f"你是一只功夫小猫，你的主人是{user_name},年龄{user_age}"

agent = create_agent(
    model=model,
    tools=[get_current_time],
    middleware=[personalized_prompt],
    context_schema=ContextSchema
)

res = agent.invoke(
    {"messages": [{"role": "user", "content": "你知道我的哪些基本信息，我和你的关系是什么"}]},
    context=ContextSchema(user_name="Dreamt",user_age=25)
)

print(res,"\n")

for msg in res["messages"]:
    msg.pretty_print()
