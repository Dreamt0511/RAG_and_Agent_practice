from langchain_core.chat_history import InMemoryChatMessageHistory

# 创建一个历史记录对象
history = InMemoryChatMessageHistory()

# 添加消息
history.add_user_message("你好，我叫小明")
history.add_ai_message("你好小明，有什么可以帮你的？")
history.add_user_message("今天天气怎么样？")
history.add_ai_message("抱歉，我暂时无法查询天气。")

# 获取所有消息
messages = history.messages
for msg in messages:
    print(f"{msg}\n")
print(messages)
# 输出: [HumanMessage(...), AIMessage(...), HumanMessage(...), AIMessage(...)]

# 获取最新消息
last_message = history.messages[-1]
print(last_message.content)  # "抱歉，我暂时无法查询天气。"