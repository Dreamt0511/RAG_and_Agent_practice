import os

from langchain.agents import create_agent
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.tools import tool


@tool(description="可以根据地理位置返回第二天的天气信息")
def get_des(location) -> str:
    return "艳阳天"


@tool(description="可以根据地理位置返回天气信息")
def get_weather(location) -> str:
    return "雨天"


agent = create_agent(
    model=ChatTongyi(model="qwen3-max", api_key=os.getenv("DASHSCOPE_API_KEY")),
    tools=[get_des, get_weather],
    system_prompt="你是一个智能助手，可以调用工具，如果能调用工具请告诉我思考过程，不能的话告诉用户不能做到"
)

result = agent.stream(
    {
        "messages": [
            {"role": "user", "content": "北京今天和明天的天气如何"}
        ]
    },
    stream_mode="values"
)
for chunk in result:
    latest_message = chunk["messages"][-1]
    print(latest_message)
    if latest_message.content:
        print(f"【{type(latest_message).__name__}】",latest_message.content)
    try:
        if latest_message.tool_calls:
            for tool in latest_message.tool_calls:
                print(f"工具调用{tool['name']}")
    except:
        pass
    print("="*140,"\n")


