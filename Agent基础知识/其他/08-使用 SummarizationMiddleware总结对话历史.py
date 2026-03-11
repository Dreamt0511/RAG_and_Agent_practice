from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_models.tongyi import ChatTongyi

main_model = ChatTongyi(model="qwen3-max")
summarize_model = ChatTongyi(model="qwen-plus")

checkpointer = InMemorySaver()

agent = create_agent(
    model=main_model,
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model=summarize_model,
            trigger=("tokens", 4000),
            keep=("messages", 3)
        )
    ],
    checkpointer=checkpointer,
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}
agent.invoke({"messages": "hi, my name is bob"}, config)
agent.invoke({"messages": "write a short poem about cats"}, config)
agent.invoke({"messages": "now do the same but for dogs"}, config)
final_response = agent.invoke({"messages": "我们一共聊了哪些话题，你的回答是什么，原封不动的给我看看"}, config)

final_response["messages"][-1].pretty_print()
