"""
RAGSystem 模块

功能说明：
- 基于 Chroma 向量数据库实现文档检索
- 使用 DashScope(OpenAI-compatible) Embedding API 进行向量召回
- 使用本地 CrossEncoder（二次精排模型）对召回结果进行重排序
- 返回与用户问题最相关的文档片段，供上层 LLM 使用
"""

import chromadb
import os
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from sentence_transformers import CrossEncoder


# =================================================
# 加载 .env 文件中的环境变量
# =================================================
load_dotenv('asst.env')
openai_api_key = os.getenv("OPENAI_API_KEY")
api_base_url = os.getenv("API_BASE_URL")
rerank_model = os.getenv("RERANK_MODEL")

# =================================================
# RAGSystem：负责向量召回 + 二次精排
# 对外提供 retrieval_chunks 方法
# =================================================
class RAGSystem:
    def __init__(
        self,
        host = "localhost",
        port=8081,
        collection_name="my_collection",  # 向量集合名称
        rerank_model_path=rerank_model,  # 本地二次精排模型路径
    ):
        # 初始化 Chroma 客户端
        chroma_client = chromadb.HttpClient(host=host, port=port)

        # 获取 / 创建向量集合
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-v4",
                api_base=api_base_url,
                api_type="dashscope",
            ),
        )

        # 加载本地 CrossEncoder 二次精排模型
        self.model = CrossEncoder(rerank_model_path)

    # =================================================
    # 根据用户问题检索相关文档片段
    # =================================================
    def retrieval_chunks(
        self,
        question,
        n_results=30,  # 向量召回数量
        rerank=True,  # 是否启用二次精排
        rank_threshold=0.2,  # 精排得分阈值
        top_k=5,  # 最终返回的文档片段数量
    ):

        # 向量召回
        result = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )

        documents = result["documents"][0]
        metadatas = result["metadatas"][0]

        # 不启用二次精排
        if not rerank:
            return {
                "documents": documents[:top_k],
                "metadatas": metadatas[:top_k],
            }

        print("向量召回数量:", len(documents))

        # 二次精排
        ranks = self.model.rank(
            question,
            documents,
            return_documents=True
        )

        chunks, metas = [], []
        for rank in ranks:
            # 得分过低或数量达到上限即停止
            if rank["score"] < rank_threshold or len(chunks) >= top_k:
                break

            chunks.append(rank["text"])
            metas.append(metadatas[rank["corpus_id"]])

        return {
            "documents": chunks,
            "metadatas": metas,
        }
