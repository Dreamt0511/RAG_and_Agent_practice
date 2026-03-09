from langchain_core.tools import tool
from langchain_community.document_loaders import TextLoader

loader = TextLoader(file_path="./data/AI时代不会淘汰程序员的原因.txt",encoding='utf-8')
docs = loader.load()


"""
content_and_artifact这个参数让工具能够区分返回值的用途：一部分给LLM看（content），一部分给系统用（artifact）。
content → 给最终用户（人类阅读/显示）
artifact → 给系统/程序（后续流程处理）
没有content_and_artifact这个标志依旧返回两个的话就会导致在传递给llm时把原始数据和出来后的数据都传了，浪费token
把这个参数当作一个标志就行（这是针对既要传递处理后的数据又要元数据的情况）
"""
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = docs#这里应该是检索出来的文档列表,list[Document]类型，先用上面加载的docs代替
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

