from pymilvus import MilvusClient, DataType, Function, FunctionType

# 1. 连接到 Milvus 服务
client = MilvusClient(
    uri="http://localhost:19530",
    token="myuser:mypassword"  # 自定义的用户名和密码
)

# 2. 创建 Schema
schema = client.create_schema()

# 添加主键字段
schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)

# 添加文本字段（存储原始文本，启用分析器）
schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=1000, enable_analyzer=True)

# 添加稀疏向量字段（存储 BM25 生成的稀疏嵌入）
schema.add_field(field_name="sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)

# 3. 定义 BM25 函数
bm25_function = Function(
    name="text_bm25_emb",
    input_field_names=["text"],
    output_field_names=["sparse"],
    function_type=FunctionType.BM25,
)

schema.add_function(bm25_function)

# 4. 配置索引参数
index_params = client.prepare_index_params()

index_params.add_index(
    field_name="sparse",
    index_type="SPARSE_INVERTED_INDEX",
    metric_type="BM25",
    params={
        "inverted_index_algo": "DAAT_MAXSCORE",
        "bm25_k1": 1.2,
        "bm25_b": 0.75
    }
)

# 5. 创建集合
client.create_collection(
    collection_name='my_collection',
    schema=schema,
    index_params=index_params
)

# 6. 插入文本数据（BM25 函数会自动生成对应的稀疏向量）
client.insert('my_collection', [
    {'text': 'information retrieval is a field of study.'},
    {'text': 'information retrieval focuses on finding relevant information in large datasets.'},
    {'text': 'data mining and information retrieval overlap in research.'},
])

# 7. 执行全文搜索
res = client.search(
    collection_name='my_collection',
    data=['whats the focus of information retrieval?'],
    anns_field='sparse',
    output_fields=['text'],  # 只返回原始文本字段，不能返回 sparse 字段
    limit=3,
)

# 8. 打印搜索结果
print(res)


"""
参考链接https://milvus.io/docs/zh/full-text-search.md
流程说明：
连接配置：连接到本地的 Milvus 服务（端口 19530）

Schema 定义：
id：主键字段，自动生成
text：存储原始文本的 VARCHAR 字段，启用分析器
sparse：存储 BM25 生成的稀疏嵌入向量

BM25 函数：将 text 字段转换为稀疏向量并存储到 sparse 字段

索引配置：为稀疏向量字段创建倒排索引，使用 BM25 距离度量

创建集合：使用定义的 schema 和索引参数创建集合

插入数据：只需提供原始文本，系统自动生成稀疏向量

全文搜索：使用自然语言查询，返回按 BM25 相关性排序的结果

输出：搜索结果包含匹配的文档内容和相关性分数

"""