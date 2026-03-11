import os
import datetime
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.agents import create_agent
from langchain_core.tools import tool

model = ChatTongyi(model = "qwen-max",api_key=os.getenv("DASHSCOPE_API_KEY"))

@tool(description="查询当前时间的工具")
def get_current_time() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


agent = create_agent(
    model=model,
    system_prompt= "你是一个全能的助手，能够调用已有的工具，如果没有可用工具，请回答：我无法调用对应工具查询您所需要的信息",
    tools= [get_current_time],
)

#保险写法
# res = agent.invoke({"messages":[
#     {"role":"user","content":"帮我查一下重庆现在的时间"}
# ]})

#新写法
res = agent.invoke({"messages":"帮我查一下重庆现在的时间"})


# message = res["messages"][-1].content
# print(res)
# print(f"\nAI回答:{message}")

#使用pretty_print()输出
for msg in res["messages"]:
    msg.pretty_print()
