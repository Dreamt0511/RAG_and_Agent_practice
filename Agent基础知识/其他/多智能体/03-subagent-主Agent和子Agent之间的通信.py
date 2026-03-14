"""
1.子Agent的输入定制：
要解决的问题：默认情况下，子Agent只接收用户的查询（query）。但有时候子Agent需要更多上下文才能更好地完成任务。
核心思想：从主Agent的状态（state）中提取额外信息，传递给子Agent，state = runtime.state
实际应用场景
传递完整对话历史：让子Agent了解之前的对话内容
传递之前任务的执行结果：让子Agent基于前序工作继续
传递用户偏好或配置：如语言偏好、输出格式要求等
传递元数据：如任务ID、时间戳、优先级等


2.子Agent的输出定制：
两种策略
策略1：通过提示词控制（Prompt the sub-agent）
python
# 在子Agent的系统提示词中明确要求
research_agent = create_agent(
    prompt= '''你是一个研究专家。完成任务后，请按以下格式返回：
    1. 研究结论摘要
    2. 关键数据点
    3. 信息来源
    这样主Agent才能充分理解你的工作。'''
)
适用场景：简单、不需要代码修改的情况


策略2：通过代码格式化（Format in code）
from langgraph.types import Command
from langchain.tools import InjectedToolCallId

@tool("subagent1_name")
def call_subagent1(
    query: str,
    tool_call_id: Annotated[str, InjectedToolCallId],  # 工具调用ID，用于关联响应
) -> Command:
    result = subagent1.invoke({
        "messages": [{"role": "user", "content": query}]
    })

    # 返回Command对象，可以同时更新多个内容
    return Command(update={
        # 更新主Agent的状态（传递额外信息）
        "example_state_key": result["example_state_key"],
        "research_summary": extract_summary(result),
        "sources": result["sources"],

        # 更新消息（必须有ToolMessage）
        "messages": [
            ToolMessage(
                content=result["messages"][-1].content,  # 子Agent的最终回复
                tool_call_id=tool_call_id  # 关联到原来的工具调用
            )
        ]
    })
适用场景：需要结构化返回、需要更新主Agent状态、需要传递多个数据

Command的作用:Command是一个特殊对象，允许你：
更新主Agent的状态：添加新的状态键值对
发送消息：必须包含ToolMessage
控制流程：可以指定下一步要做什么
"""