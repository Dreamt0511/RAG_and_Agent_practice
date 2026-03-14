"""
https://docs.langchain.com/oss/python/langchain/multi-agent/subagents#tool-per-agent
"""

from langchain.tools import tool
from langchain.agents import create_agent

#创建代理
subagent1 = create_agent(model="",tools=[])
subagent2 = create_agent(model="",tools=[])

#把代理包装成工具
@tool("subagent1_name",description="subagent1_description")
def call_subagent1(query):
    res = subagent1.invoke({"messages":[{"role":"user","content":query}]})
    return (res["messages"][-1].content


@tool("subagent2_name",description="subagent2_description"))
def call_subagent2(query):
    res = subagent2.invoke({"messages":[{"role":"user","content":query}]})
    return res["messages"][-1].content

#创建main-agent
main_agent = create_agent(
    model="",
    tools=[call_subagent1,call_subagent2]
)

"""
总结
维度	    Tool_per_agent	Single dispatch
工具数量	多个工具	一个工具
选择方式	通过选择不同的工具	    通过工具参数
描述粒度	每个工具可详细描述	    工具描述+参数说明
扩展性	需要修改主代理代码	    只需更新注册表
定制化	高，可定制每个子代理	低，统一调用约定
适用场景	子代理少、需要精细控制	子代理多、分布式团队

所以，关键区别不是"谁做选择"（都是主代理做选择），而是"选择以什么形式体现"：
Tool per agent：选择体现在"选哪个工具"
Single dispatch：选择体现在"给工具的哪个参数"

两种模式的核心隔离能力是相同的：
✅ 子代理在独立上下文中运行
✅ 中间步骤不污染主代理历史
✅ 只返回最终结果给主代理
✅ 防止主代理上下文爆炸
"""