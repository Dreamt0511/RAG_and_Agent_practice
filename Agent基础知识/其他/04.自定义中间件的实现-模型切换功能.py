"""
内置中间件覆盖了常见场景，但真正体现灵活性的是自定义中间件的能力。
我们举个例子，假设需要根据用户的技术水平动态调整 Agent 的能力：
参考链接：https://cloud.tencent.com/developer/article/2588400
"""

from dataclasses import dataclass
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.agents.middleware.types import ModelResponse
from langchain.agents import create_agent
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.tools import tool

normal_model = ChatTongyi(model = "qwen-plus")
expert_model = ChatTongyi(model = "qwen-max")


# First, define what you want to track about users
@dataclass
class Context:
    user_expertise: str = "beginner"  # Is user a beginner or expert?

@tool
def advanced_search():
    pass


@tool
def data_analysis():
    pass

@tool
def simple_search():
    pass


@tool
def basic_calculator():
    pass

#自定义中间件，根据玩家水平（这个可以根据玩家的提问水平动态判断）切换回答的聊天模型
# Create your custom middleware
class ExpertiseBasedToolMiddleware(AgentMiddleware):
    def wrap_model_call(self,request: ModelRequest,handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
        # Check: Is this user a beginner or expert?
        user_level = request.runtime.context.user_expertise

        if user_level == "expert":
            # Experts get powerful AI and advanced tools
            model = expert_model
            tools = [advanced_search, data_analysis]
        else:
            # Beginners get simpler AI and basic tools
            model = normal_model
            tools = [simple_search, basic_calculator]

        # Update what the AI sees
        request.model = model
        request.tools = tools

        # Send it forward to the AI
        return handler(request)

# Now use your custom middleware (just like the built-in ones!)
agent = create_agent(
    model= normal_model,#默认使用普通模型
    tools=[simple_search, advanced_search, basic_calculator, data_analysis],
    middleware=[ExpertiseBasedToolMiddleware()],  # Your custom middleware here!
    context_schema=Context
)

