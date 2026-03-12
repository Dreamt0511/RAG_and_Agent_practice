import os

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from pydantic import BaseModel
from langchain_community.chat_models.tongyi import ChatTongyi
model = ChatTongyi(model = "qwen-max",api_key=os.getenv("DASHSCOPE_API_KEY"))

class Weather(BaseModel):
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