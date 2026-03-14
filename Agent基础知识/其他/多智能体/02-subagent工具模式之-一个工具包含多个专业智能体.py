"""
https://docs.langchain.com/oss/python/langchain/multi-agent/subagents#single-dispatch-tool
"""

from langchain.tools import tool
from langchain.agents import create_agent

research_agent = create_agent(
    model="",
    system_prompt="你是一个研究专家，专门负责材料收集",
    tools=[]
)

writer_agent = create_agent(
    model="",
    system_prompt="你是一个写作专家，专门负责写作",
    tools=[]
)

#注册可用的代理
subagents = {
    "research":research_agent,
    "writer":writer_agent
}

@tool
def task(
        agent_name:str,
        description:str
)->str:
    """
    选择一个agent执行任务
    可用的agent有:
    - research: Research and fact-finding
    - writer: Content creation and editing
    """
    #指定agent
    agent = subagents[agent_name]
    res = agent.invoke({
        "messages":[
            {"role":"user","content":description}
        ]
    })

    return res["messages"][-1].content


main_agent = create_agent(
    model = "",
    tools=[task],
    system_prompt=(
        "你可以自由分配下面的agent "
        "research (fact-finding), "
        "writer (content creation). "
        "使用task工具去发起工作分配."
    ),
)

