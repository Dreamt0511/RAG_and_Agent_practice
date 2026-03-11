import os

import json
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import ToolMessage

model = ChatTongyi(model= "qwen-plus")
api_key = os.getenv("DASHSCOPE_API_KEY")
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


#使用"阿里云百炼_联网搜索 MCP
async def main():
    client = MultiServerMCPClient({
        "WebSearch": {
            "transport": "http",  # 或 "http"，根据实际支持的协议
            "url": "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp",
            "headers": {
                "Authorization": f"Bearer {api_key}"  # 去掉$符号
            },
            # 可选：添加超时设置
            "timeout": 30
        }
    })

    tools = await client.get_tools()
    agent = create_agent(
        model = model,
        tools= tools
    )

    q = "langgraph需要学习哪些知识才能做项目"
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": q}]}
    )

    last_message = result["messages"][-1]
    last_message.pretty_print()
    print(f"问题{q}")
    print("\n=================== 参考来源如下👇 =============================")
    # 在你的代码后面添加
    for message in result["messages"]:
        if isinstance(message, ToolMessage):
            # ToolMessage 的 content 里包含 JSON 字符串
            if message.content:
                try:
                    # 注意：message.content 是一个列表，第一个元素包含 JSON
                    if isinstance(message.content, list) and len(message.content) > 0:
                        # 提取 JSON 字符串
                        json_str = message.content[0].get('text', '')
                        search_results = json.loads(json_str)


                        print(f"状态码: {search_results.get('status')}")
                        print(f"请求ID: {search_results.get('request_id')}")

                        # 提取 pages 数组（这就是搜索到的结果）
                        pages = search_results.get('pages', [])
                        print(f"\n共找到 {len(pages)} 条搜索结果")

                        # 遍历每条搜索结果
                        for i, page in enumerate(pages, 1):
                            print(f"\n--- 结果 {i} ---")
                            print(f"标题: {page.get('title')}")
                            print(f"来源: {page.get('hostname')}")
                            print(f"链接: {page.get('url')}")
                            print(f"摘要: {page.get('snippet')[:100]}...")  # 只显示前100字符

                except Exception as e:
                    print(f"解析出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())

