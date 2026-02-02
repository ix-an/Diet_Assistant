import chromadb
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import json
import hashlib

chroma_client = chromadb.HttpClient(host="localhost", port=8081)

collection = chroma_client.get_or_create_collection(
    name="my_collection",
    embedding_function=OpenAIEmbeddingFunction(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model_name="text-embedding-v4",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_type="dashscope"
    )
)

if __name__ == "__main__":

    chunks_path = "./chunks/knowledges.json"

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        print(chunks)
        ids,documents,metadatas = [],[],[]
        for chunk in chunks:
            ids.append(hashlib.md5((chunk["content"] + str(chunk["metadata"])).encode('utf-8')).hexdigest())
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])
    collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
)
print(collection.count())