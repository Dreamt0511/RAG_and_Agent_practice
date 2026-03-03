"""
RAG 企业知识库系统：让大模型读懂你的私有数据
项目来源https://cloud.tencent.com/developer/article/2620399

"""

import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
"""
由于示例需要from langchain.chains import RetrievalQA这样导入RetrievalQA方便后面创建rag链，
但是新版的langchain中已经找不到Langchain.chain开头的模块了，所以暂时不做
"""