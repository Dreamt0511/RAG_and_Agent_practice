"""
通过中间件监控工具执行过程中的错误
发生错误后返沪错误消息提示AI检查输入重试
参考链接
https://docs.langchain.com/oss/python/migrate/langchain-v1
"""
# 只处理由于无效输入导致的工具执行错误
# 这些输入通过了schema验证但在运行时失败（例如，无效的SQL语法）
# 不处理：
# - 网络故障（应使用工具重试中间件处理）
# - 工具实现错误（应该向上抛出）
# - schema不匹配错误（已由框架自动处理）


from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.prebuilt.tool_node import ToolCallRequest
from typing import Callable
from langgraph.types import Command

model = ChatTongyi(model="qwen-plus")


@wrap_tool_call
# 工具执行的监控
def handle_tool_errors(request: ToolCallRequest,
                       handler: Callable[[ToolCallRequest], ToolMessage | Command], ) -> ToolMessage | Command:
    """Handle tool execution errors with custom messages."""
    try:
        # 正常直接返回
        return handler(request)
    except Exception as e:
        """    
        Only handle errors that occur during tool execution due to invalid inputs
        that pass schema validation but fail at runtime (e.g., invalid SQL syntax).
        Do NOT handle:
        - Network failures (use tool retry middleware instead)
        - Incorrect tool implementation errors (should bubble up)
        - Schema mismatch errors (already auto-handled by the framework)
    
        Return a custom error message to the model
        """
        return ToolMessage(
            content=f"工具执行错误，请检查你的输入然后重试【{str(e)}】",
            tool_call_id = request.tool_call["id"]
        )

agent = create_agent(
    model = model,
    tools=[],
    middleware=[handle_tool_errors]
)
