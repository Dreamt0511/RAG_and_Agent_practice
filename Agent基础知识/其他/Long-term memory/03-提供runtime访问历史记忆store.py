from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.runtime import Runtime
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage
from dataclasses import dataclass
from typing import TypedDict, List, Sequence
import os
import time


# 1. 定义上下文（包含用户信息）
@dataclass
class Context:
    user_id: str
    user_name: str = "访客"


# 2. 定义状态
class ChatState(TypedDict):
    messages: List[dict]  # 对话历史
    response: str


# 3. 初始化大模型
model = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY")
)


# 4. 创建节点函数（带Runtime和大模型）
async def process_with_llm(
        state: ChatState,
        runtime: Runtime[Context]  # LangGraph自动注入
):
    # 获取用户信息和存储
    user_id = runtime.context.user_id
    user_name = runtime.context.user_name
    store = runtime.store

    print(f"\n--- 处理用户 {user_name}({user_id}) 的消息 ---")

    # 获取用户的最新消息
    last_message = state["messages"][-1]["content"]
    print(f"用户消息: {last_message}")

    # 1. 从存储中检索相关记忆（语义搜索）
    memories = await store.asearch(
        (user_id, "memories"),
        query=last_message,  # 基于当前消息搜索相关记忆
        limit=5
    )

    # 2. 构建记忆上下文
    memory_context = ""
    if memories:
        memory_context = "以下是关于这个用户的一些历史记忆：\n"
        for i, mem in enumerate(memories, 1):
            memory_context += f"{i}. {mem.value['content']} (重要程度: {mem.value.get('importance', 5)}/10)\n"
        print(f"找到 {len(memories)} 条相关记忆")
    else:
        print("没有找到相关记忆")

    # 3. 构建系统提示
    system_prompt = f"""你是一个友好的AI助手，正在和用户 {user_name} 对话。

{memory_context}

基于以上记忆，用温暖、个性化的方式回应用户。如果记忆中有相关信息，请引用它们来展示你记得用户。
如果没有相关记忆，就正常对话，并在对话中自然地了解用户。
"""

    # 4. 调用大模型生成回复
    messages = [
        {"role": "system", "content": system_prompt},
        *state["messages"][-5:]  # 只取最近5条消息作为上下文
    ]

    response = await model.ainvoke(messages)
    ai_response = response.content
    print(f"AI回复: {ai_response}")

    # 5. 分析对话，提取重要信息保存为记忆
    await extract_and_save_memories(store, user_id, last_message, ai_response)

    return {"response": ai_response}


# 5. 提取并保存记忆的辅助函数
async def extract_and_save_memories(store, user_id: str, user_msg: str, ai_msg: str):
    """分析对话并保存重要信息到记忆存储"""

    # 这里简化了，实际可以用另一个LLM来提取关键信息
    memories_to_save = []

    # 检测偏好信息
    preferences_keywords = ["我喜欢", "我爱", "我讨厌", "我不喜欢", "我最爱"]
    for keyword in preferences_keywords:
        if keyword in user_msg:
            memory = {
                "content": f"用户偏好: {user_msg}",
                "type": "preference",
                "importance": 8,
                "timestamp": time.time()
            }
            memories_to_save.append(memory)

    # 检测个人信息
    if "我叫" in user_msg or "我是" in user_msg:
        memory = {
            "content": f"用户信息: {user_msg}",
            "type": "personal_info",
            "importance": 9,
            "timestamp": time.time()
        }
        memories_to_save.append(memory)

    # 保存到存储
    for memory in memories_to_save:
        key = f"memory_{int(time.time())}_{len(memories_to_save)}"
        await store.aput(
            namespace=(user_id, "memories"),
            key=key,
            value=memory,
            index=["content"]  # 只索引content字段用于搜索
        )
        print(f"✅ 保存新记忆: {memory['content'][:50]}...")


# 6. 构建图
builder = StateGraph(ChatState)
builder.add_node("chat", process_with_llm)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

# 7. 编译带存储的图
store = InMemoryStore()  # 记忆存储
checkpointer = InMemorySaver()  # 对话历史检查点
graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)


# 8. 测试函数
async def test_chatbot():
    # 创建两个不同的用户
    users = {
        "alice": Context(user_id="user_001", user_name="爱丽丝"),
        "bob": Context(user_id="user_002", user_name="鲍勃")
    }

    # 爱丽丝的第一次对话
    print("\n" + "=" * 50)
    print("爱丽丝第一次对话")
    result1 = await graph.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "你好！我叫爱丽丝，我喜欢吃披萨和读书"}
            ]
        },
        config={"configurable": {"thread_id": "thread_1"}},
        context=users["alice"]
    )

    # 爱丽丝的第二次对话（不同线程，但同一用户）
    print("\n" + "=" * 50)
    print("爱丽丝第二次对话（新会话）")
    result2 = await graph.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "你还记得我喜欢吃什么吗？"}
            ]
        },
        config={"configurable": {"thread_id": "thread_2"}},  # 不同线程
        context=users["alice"]  # 同一用户
    )

    # 鲍勃的第一次对话
    print("\n" + "=" * 50)
    print("鲍勃第一次对话")
    result3 = await graph.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "你好，我叫鲍勃，我喜欢打篮球"}
            ]
        },
        config={"configurable": {"thread_id": "thread_3"}},
        context=users["bob"]
    )

    # 查看存储的所有记忆
    print("\n" + "=" * 50)
    print("所有用户的记忆：")

    # 查看爱丽丝的记忆
    alice_memories = await store.asearch(
        ("user_001", "memories"),
        query="*",  # 获取所有
        limit=10
    )
    print(f"\n爱丽丝的记忆 ({len(alice_memories)} 条):")
    for mem in alice_memories:
        print(f"  - {mem.value['content']} (重要: {mem.value['importance']})")

    # 查看鲍勃的记忆
    bob_memories = await store.asearch(
        ("user_002", "memories"),
        query="*",
        limit=10
    )
    print(f"\n鲍勃的记忆 ({len(bob_memories)} 条):")
    for mem in bob_memories:
        print(f"  - {mem.value['content']} (重要: {mem.value['importance']})")


# 运行测试
import asyncio

asyncio.run(test_chatbot())