md5_path = "./md5.txt"

#Chorma
collection_name = "RAG_Project"
persist_directory = "./chroma_db"

#splitter
chunk_size = 300#每段最大字符数
chunk_overlap = 50#每段之间重叠的字符数
separators=[
        "\n\n",  # 1. 优先按段落分割（两个换行）
        "\n",  # 2. 其次按行分割
        "。", "！", "？",  # 3. 再按句子分割
        "；", "，", "、",  # 4. 再按短语分割
        " ",  # 5. 再按空格
        ""  # 6. 最后按字符
    ]
max_split_char_num = 300#文本分割的阈值
