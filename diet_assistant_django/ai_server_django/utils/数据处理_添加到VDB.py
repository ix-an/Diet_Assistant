"""
ChromaDB 知识库导入脚本：将预处理的RAG知识块导入向量数据库
核心功能：将Markdown清洗分割后的JSON知识库转换为ChromaDB可检索的向量数据库
适用场景：RAG系统知识库初始化、知识库更新
"""

import chromadb  # ChromaDB核心库，用于向量数据库操作
import os  # 操作系统接口，用于环境变量和路径处理
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction  # 适配OpenAI嵌入模型的函数
import json  # JSON数据处理
import hashlib  # 生成唯一ID的哈希函数

# ========================
# 1. 连接到ChromaDB服务器
# ========================
chroma_client = chromadb.HttpClient(host="localhost", port=8081)
"""
- 创建HTTP客户端连接到本地ChromaDB服务（默认运行在8081端口）
- ChromaDB支持内存模式（调试）和持久化模式（生产），这里使用HTTP接口
- 注意：需先启动ChromaDB服务（如通过`chroma run`命令）
"""

# ========================
# 2. 创建/获取知识库集合
# ========================
collection = chroma_client.get_or_create_collection(
    name="my_collection",  # 集合名称（知识库标识）
    embedding_function=OpenAIEmbeddingFunction(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 从环境变量获取阿里云DashScope API密钥
        model_name="text-embedding-v4",  # 使用的嵌入模型（阿里云文本嵌入模型）
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云DashScope API端点
        api_type="dashscope"  # 指定API类型为DashScope
    )
)
"""
- get_or_create_collection: 如果集合已存在则获取，不存在则创建
- embedding_function: 定义如何将文本转换为向量（关键组件）
- 阿里云DashScope配置说明：
  * `text-embedding-v4`是阿里云最新嵌入模型，比v3更优
  * API端点使用`compatible-mode/v1`（与OpenAI兼容的接口，避免模型不兼容问题）
  * 通过环境变量管理密钥，避免硬编码在代码中（安全最佳实践）

"""

# ========================
# 3. 加载预处理知识库
# ========================
if __name__ == "__main__":
    chunks_path = "./chunks/knowledges.json"  # 预处理知识库JSON文件路径

    # 读取JSON文件
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)  # 加载为Python字典列表
        print(f"✅ 加载知识库: {len(chunks)} 个知识块")  # 确认加载数量

    # 初始化存储列表
    ids, documents, metadatas = [], [], []

    # 遍历每个知识块
    for chunk in chunks:
        # 生成唯一ID（防止重复添加）
        # 1. 拼接内容+元数据（确保不同内容/元数据组合有唯一ID）
        # 2. MD5哈希（128位哈希，足够唯一且高效）
        # 3. hexdigest()转换为16进制字符串（符合ChromaDB要求）
        unique_id = hashlib.md5(
            (chunk["content"] + str(chunk["metadata"])).encode('utf-8')
        ).hexdigest()
        ids.append(unique_id)

        # 提取文档内容
        documents.append(chunk["content"])

        # 提取元数据（如来源文件、部门等）
        metadatas.append(chunk["metadata"])

    # ========================
    # 4. 将数据添加到ChromaDB
    # ========================
    collection.add(
        ids=ids,  # 唯一ID列表
        documents=documents,  # 文本内容列表
        metadatas=metadatas,  # 元数据列表（用于后续过滤）
    )

    # ========================
    # 5. 确认导入结果
    # ========================
    print(f"📊 知识库统计: {collection.count()} 个文档已导入")  # 打印集合中文档总数
    print(f"🔍 首个文档示例: {documents[0][:50]}...")  # 打印第一个文档的前50字符