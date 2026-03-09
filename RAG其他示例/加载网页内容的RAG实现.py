"""
这个主要是爬取网页内容然后进行rag
参考链接：https://docs.langchain.com/oss/python/langchain/rag#expand-for-full-code-snippet
"""

import bs4
import os
from fake_useragent import UserAgent
from langchain_community.document_loaders import WebBaseLoader
import requests
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 创建不验证SSL的session
session = requests.Session()
session.verify = False

# 获取随机UA
ua = UserAgent()
random_ua = ua.random

# 设置环境变量
os.environ['USER_AGENT'] = random_ua

# 只解析网页文章标题，副标题，文章主体内容
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))

loader = WebBaseLoader(
    web_path="https://lilianweng.github.io/posts/2023-06-23-agent/",
    bs_kwargs={"parse_only": bs4_strainer},
    header_template={'User-Agent': random_ua},
    requests_kwargs={'verify': False}  # 添加这行禁用SSL验证，在loader中禁用SSL验证
)

docs = loader.load()

# 确认只加载了一个文档
assert len(docs) == 1
print(f"从网页加载的内容为：{docs[0].page_content[:1000]}")#取前1000个字符
print(f"文档长度：{len(docs[0].page_content)} 字符")
print(f"\n文档元数据：{docs[0].metadata}")

