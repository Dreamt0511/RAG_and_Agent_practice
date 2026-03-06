from langchain_chroma import Chroma
import config_data as config
"""返回向量检索器，方便加入链"""


class VectorStoreService():

    def __init__(self,embedding):
        self.vector_store = Chroma(
            collection_name= config.collection_name,
            persist_directory= config.persist_directory,
            embedding_function= embedding
        )

    def get_retriever(self):
        retriever = self.vector_store.as_retriever(search_kwargs = {"k":config.similarity_threshold})
        return retriever