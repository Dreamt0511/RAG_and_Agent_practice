"""
https://docs.langchain.com/oss/python/langchain/long-term-memory#read-long-term-memory-in-tools

!!! example "Examples"
        Basic key-value storage:
            store = InMemoryStore()
            store.put(("users", "123"), "prefs", {"theme": "dark"})
            item = store.get(("users", "123"), "prefs")

        Vector search with embeddings:
            from langchain.embeddings import init_embeddings
            store = InMemoryStore(index={
                "dims": 1536,
                "embed": init_embeddings("openai:text-embedding-3-small"),
                "fields": ["text"],
            })

            # Store documents
            store.put(("docs",), "doc1", {"text": "Python tutorial"})
            store.put(("docs",), "doc2", {"text": "TypeScript guide"})

            # Search by similarity
            results = store.search(("docs",), query="python programming")

    Note:
        Semantic search is disabled by default. You can enable it by providing an `index` configuration
        when creating the store. Without this configuration, all `index` arguments passed to
        `put` or `aput`will have no effect.

    Warning:
        This store keeps all data in memory. Data is lost when the process exits.
        For persistence, use a database-backed store like PostgresStore.

    Tip:
        For vector search, install numpy for better performance:
        ```bash
        pip install numpy

"""
import time
from dataclasses import dataclass

from langchain_community.chat_models import ChatTongyi
from langchain_core.runnables import RunnableConfig
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore


model = ChatTongyi(model="qwen3-max")

@dataclass
class Context:
    user_id: str

# InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production.
store = InMemoryStore()

# Write sample data to the store using the put method
store.put(
    ("users",),  # Namespace to group related data together (users namespace for user data)
    "user_123",  # Key within the namespace (user ID as key)
    {
        "name": "John Smith",
        "language": "English",
    }, # Data to store for the given user
)

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Look up user info."""
    # Access the store - same as that provided to `create_agent`
    store = runtime.store
    user_id = runtime.context.user_id

    # Retrieve data from store - returns StoreValue object with value and metadata
    user_info = store.get(("users",), user_id)
    print(user_info)
    print(f"\n\nuser_info的类型为{type(user_info)}\n\n")

    """
    user_info的格式：
    Item(namespace=['users'], key='user_123', 
    value={'name': 'John Smith', 'language': 'English'},
     created_at='2026-03-11T08:04:40.245346+00:00', 
     updated_at='2026-03-11T08:04:40.245346+00:00')
    """
    return str(user_info.value) if user_info else "Unknown user"

agent = create_agent(
    model=model,
    tools=[get_user_info],
    # Pass store to agent - enables agent to access store when running tools
    store=store,
    context_schema=Context
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "look up user information"}]},
    context=Context(user_id="user_123")
)