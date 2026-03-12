"""
这只是一个结构化输出的示例
规定结构化输出的前提是模型提供这种支持
下面使用的千问模型就不支持
因此不支持结构化输出的模型，可以自己自定义结构化输出
"""
import os
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy,ToolStrategy
from langchain_core.tools import tool
from pydantic import BaseModel
from langchain_community.chat_models.tongyi import ChatTongyi
model = ChatTongyi(model = "qwen-max",api_key=os.getenv("DASHSCOPE_API_KEY"))

class Weather(BaseModel):
    messages : list
    temperature: float
    condition: str

@tool
def weather_tool(city: str) -> str:
    """Get the weather for a city."""
    return f"it's sunny and 70 degrees in {city}"

agent = create_agent(
    model = model,
    tools=[weather_tool],
    response_format=ToolStrategy(Weather)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in SF?"}]
})

print(result)
print("="*100)
print(repr(result["structured_response"]))
# results in `Weather(temperature=70.0, condition='sunny')`


#如果模型支持，使用ProviderStrategy,ToolStrategy规定下的结构化输出的结果大概如下所示

"""
{
    'messages': [
        HumanMessage(content="What's the weather in Shanghai?"),
        AIMessage(
            content='',  # 内容为空
            tool_calls=[
                {
                    'name': 'get_weather',  # 实际的天气工具
                    'args': {'city': 'Shanghai'},
                    'id': 'call_123'
                },
                {
                    'name': 'WeatherInfo',  # 自动创建的结构化输出工具
                    'args': {
                        'temperature': 22.0,
                        'condition': 'sunny',
                        'humidity': 65,
                        'wind_speed': 10.0
                    },
                    'id': 'call_456'
                }
            ]
        ),
        ToolMessage(content='Weather in Shanghai: 22°C, sunny, humidity 65%, wind 10km/h', tool_call_id='call_123'),
        ToolMessage(
            content='',  # 结构化输出的工具调用结果为空
            tool_call_id='call_456',
            artifact=WeatherInfo(
                temperature=22.0,
                condition='sunny',
                humidity=65,
                wind_speed=10.0
            )
        )
    ],
    'structured_response': WeatherInfo(
        temperature=22.0,
        condition='sunny',
        humidity=65,
        wind_speed=10.0
    )
}
"""
