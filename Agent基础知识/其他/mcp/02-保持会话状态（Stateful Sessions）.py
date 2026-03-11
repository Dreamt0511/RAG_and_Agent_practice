from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
import asyncio

"""
# 默认行为：每次调用都是独立的
async with MultiServerMCPClient({...}) as client:
    # 调用1：创建新会话 → 执行 → 销毁
    result1 = await client.call_tool("server", "tool1", args)
    
    # 调用2：又创建新会话 → 执行 → 销毁
    result2 = await client.call_tool("server", "tool2", args)
    # 两次调用之间没有任何关联，不共享任何状态
"""


async def main():
    config =   {
        #toolkit_1,toolkit_2是自定义的服务器标识名（也可以理解为工具集名），不是工具本身。
            "toolkit_1": {
                "transport": "stdio",  # Local subprocess communication
                "command": "python",
                # Absolute path to your math_server.py file
                "args": ["/path/to/math_server.py"],
            },
            "toolkit_2": {
                "transport": "http",  # HTTP-based remote server
                # Ensure you start your weather server on port 8000
                "url": "http://localhost:8000/mcp",
            }
        }
    async with MultiServerMCPClient(config) as client:
        async with client.session("toolkit_1") as session:
            # 第一次对话
            response1 = await session.call_tool("tool_name1", {
                "message": "我的名字是张三"
            })
            # 服务器记住了"张三"

            # 第二次对话（同一会话）
            response2 = await session.call_tool("tool_name2", {
                "message": "我叫什么名字？"
            })
            # 服务器应该能回答"张三"


