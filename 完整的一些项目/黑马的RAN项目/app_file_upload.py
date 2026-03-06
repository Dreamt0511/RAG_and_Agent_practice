"""基于streamlit的Web文件上传服务"""
import time

import streamlit as st
#由于streamlit的刷新机制，每次页面元素发生变化，代码就会重新执行一遍，导致状态丢失，因此可以使用st.session_state来管理状态，session_state就是一个字典dict
#利用session_state存储KnowledgeBaseService实例可以避免重复创建实例
from konwlege_base import KnowledgeBaseService
from tornado.gen import sleep

#添加网页标题
st.title("知识库上传服务")

#获取上传的文件对象
uploader_file = st.file_uploader(
    "请上传.txt文件",
    type= ["txt"],
    accept_multiple_files= False#一次只允许上传一个文件
)
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploader_file is not None:
    #提取文件信息
    file_name = uploader_file.name
    file_size = uploader_file.size / 1024
    file_type = uploader_file.type
    # 获得文件内容
    text = uploader_file.getvalue().decode("utf-8")

    #显示上传的文件信息
    st.subheader(f"文件名：{file_name}")
    st.write(f"文件格式：{file_type} | 大小：{file_size:.2f} kb")

    # 使用expander折叠面板，点击展开显示内容
    with st.expander("查看文件内容"):
        st.text(text)

    #使用转圈动画，然后显示加载结果
    with st.spinner("载入数据库中..."):
        time.sleep(0.1)
        result = st.session_state["service"].upload_to_chroma_by_str(text,file_name)
        st.write(result)


