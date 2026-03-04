from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage


def print_prompt(messages):
    """打印提示信息用于调试"""
    print("=" * 20, f"当前提示信息{messages.to_string()}", "=" * 20)
    return messages


# 初始化模型
model = ChatTongyi(model="qwen3-max")

# 使用ChatPromptTemplate创建更结构化的提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的助手，需要根据对话历史来回应用户的问题。"),
    MessagesPlaceholder(variable_name="chat_history"),  # 历史消息占位符
    ("human", "{input}")  # 用户当前输入
])

# 构建基础链
base_chain = prompt | print_prompt | model | StrOutputParser()

# 历史记录存储
chat_history_store = {}


def get_history(session_id: str):
    """获取或创建会话历史记录"""
    if session_id not in chat_history_store:
        chat_history_store[session_id] = InMemoryChatMessageHistory()
    return chat_history_store[session_id]


# 创建带历史记录的对话链
conversation_chain = RunnableWithMessageHistory(
    base_chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

if __name__ == '__main__':
    # 配置会话ID
    session_config = {"configurable": {"session_id": "user_001"}}

    # 测试对话
    print("第一次对话：")
    response1 = conversation_chain.invoke(
        {"input": "小明有一只猫"},
        session_config
    )
    print(f"助手回复：{response1}\n")

    print("第二次对话：")
    response2 = conversation_chain.invoke(
        {"input": "小刚有两只狗"},
        session_config
    )
    print(f"助手回复：{response2}\n")

    print("第三次对话：")
    response3 = conversation_chain.invoke(
        {"input": "他们共有几只宠物？"},
        session_config
    )
    print(f"助手回复：{response3}")