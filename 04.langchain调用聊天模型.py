from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

model = ChatTongyi(model="qwen-plus")

messages = [
    SystemMessage("你是一只功夫小猫"),
    AIMessage("妈咪妈咪哄，我是。。。"),
    HumanMessage("回答按照上面的格式开始"),
    HumanMessage("你是谁")

]

res = model.stream(input=messages)
for chunk in res:
    print(chunk.content, end="", flush=True)
