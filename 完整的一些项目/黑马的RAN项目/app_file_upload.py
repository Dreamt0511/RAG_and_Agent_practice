"""基于streamlit的Web文件上传服务"""
import streamlit as st

#添加网页标题
st.title("知识库上传服务")

#获取上传的文件对象
uploader_file = st.file_uploader(
    "请上传.txt文件",
    type= ["txt"],
    accept_multiple_files= False#一次只允许上传一个文件
)

if uploader_file is not None:
    #提取文件信息
    file_name = uploader_file.name
    file_size = uploader_file.size / 1024
    file_type = uploader_file.type

    #显示上传的文件信息
    st.subheader(f"文件名{file_name}")
    st.write(f"文件格式：{file_type} | 大小：{file_size:.2f} kb")

    text = uploader_file.getvalue().decode("utf-8")
    st.write(text)

