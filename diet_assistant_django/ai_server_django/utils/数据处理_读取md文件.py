"""
RAG知识库预处理模块：将Markdown文档清洗、语义分割、合并后生成结构化知识块
核心流程：格式清洗 → 语义分割 → 分块优化 → JSON持久化
适用场景：构建高质量RAG知识库前的数据预处理
"""

import json
import re
from pathlib import Path
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class MarkdownRAGProcessor:
    """
    Markdown文档RAG预处理器
    功能：清洗Markdown噪声 → 调用语义分割模型 → 合并短文本块 → 生成标准化知识库JSON
    """

    def __init__(self, model_path="./segmentation-models", min_chunk_length=120):
        """
        初始化处理器

        Args:
            model_path (str): ModelScope文档分割模型本地路径（需提前下载）
            min_chunk_length (int): 合并后单个知识块的最小字符长度（防碎片化）
        """
        # 加载ModelScope文档语义分割pipeline（支持中文文档结构理解）
        self.pipeline = pipeline(
            task=Tasks.document_segmentation,  # 任务类型：文档分割
            model=model_path,  # 模型路径
            model_revision="master",  # 模型版本
        )
        self.min_chunk_length = min_chunk_length

        # 占位符设计说明：
        # - 移除句号保护（__DOT__）：保留原始标点利于模型识别语义边界
        # - 仅保护换行符：避免pipeline将换行误判为分割点导致语义断裂
        self.newline_placeholder = "__NEWLINE__"

    def _clean_markdown(self, text):
        """
        清洗Markdown噪声元素（保留语义结构，移除干扰项）

        处理逻辑：
        1. 移除图片链接（含images/路径的特殊格式）
        2. 清除水平分割线（---）
        3. 规范化空格（连续空格→单空格）
        4. 清理表格属性中的引号（如 align="center" → align=center）

        Args:
            text (str): 原始Markdown文本
        Returns:
            str: 清洗后的纯文本（保留标题/列表/表格结构符号）
        """
        # 移除标准Markdown图片语法 ![alt](url)
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        # 移除特定路径图片（如本地存储的images/目录图片）
        text = re.sub(r"\[.*?\]\(images/.*?\)", "", text)
        # 删除独立行的水平分割线（3个以上-且前后无其他字符）
        text = re.sub(r"^-{3,}\s*$", "", text, flags=re.MULTILINE)
        # 合并连续空格为单空格
        text = re.sub(r" +", " ", text)
        # 清理表格HTML属性中的引号（避免JSON序列化冲突）
        text = re.sub(r'(\w+)="([^"]*)"', r"\1=\2", text)
        text = re.sub(r"(\w+)='([^']*)'", r"\1=\2", text)
        return text.strip()

    def _protect_text(self, text):
        """
        保护换行符：替换为占位符防止pipeline误分割

        设计原因：
        - 文档分割模型可能将换行符视为强分割点
        - 用占位符临时保留段落边界信息
        - 注意：不保护句号（保留标点利于语义分割模型判断句子结束）

        Args:
            text (str): 原始文本
        Returns:
            str: 换行符被替换的文本
        """
        return text.replace("\n", self.newline_placeholder)

    def _restore_text(self, text):
        """
        恢复文本：将占位符转为空格（非换行符！）

        关键设计：
        - 恢复为" "而非"\n"：确保分割后的文本块为连续段落
        - 避免后续嵌入模型将换行符视为特殊token干扰语义
        - 与_clean_markdown配合实现"结构保留+噪声清除"平衡

        Args:
            text (str): 含占位符的文本
        Returns:
            str: 恢复为空格分隔的连续文本
        """
        return text.replace(self.newline_placeholder, " ")

    def merge_chunks(self, chunks):
        """
        智能合并短文本块（解决模型分割过碎问题）

        策略：
        1. 跳过空块
        2. 顺序合并直到达到min_chunk_length
        3. 末尾剩余短块追加到前一块（避免孤立短句）

        Args:
            chunks (List[str]): 原始分割文本块列表
        Returns:
            List[str]: 合并优化后的文本块列表
        """
        merged = []
        current = ""
        for chunk in chunks:
            if not chunk.strip():  # 跳过空块
                continue
            # 累积当前块
            current = f"{current} {chunk}" if current else chunk

            # 达到最小长度则存入结果
            if len(current) >= self.min_chunk_length:
                merged.append(current.strip())
                current = ""

        # 处理剩余内容：追加到最后一块（避免产生超短尾块）
        if current:
            if merged:
                merged[-1] += " " + current.strip()
            else:  # 特殊情况：全文均短于阈值
                merged.append(current.strip())
        return merged

    def process_files(self, input_dir, output_file):
        """
        批量处理Markdown文件并生成知识库JSON

        流程：
        1. 遍历目录下所有.md文件
        2. 单文件处理：清洗→保护→语义分割→恢复→二次清洗→合并
        3. 构建带元数据的知识块
        4. 持久化为标准JSON

        Args:
            input_dir (str): Markdown源文件目录路径
            output_file (str): 输出JSON文件路径
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ 错误：目录 {input_dir} 不存在")
            return

        knowledges = []  # 存储所有知识块
        files = list(input_path.glob("*.md"))

        print(f"📁 开始处理 {len(files)} 个Markdown文件...")

        for file_path in files:
            try:
                # ============ 步骤1：读取原始Markdown ============
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # ============ 步骤2：预处理与语义分割 ============
                # 2.1 保护换行符（防pipeline误分割）
                protected = self._protect_text(content)
                # 2.2 调用ModelScope文档分割模型（核心：按语义切分）
                result = self.pipeline(documents=protected)
                # 2.3 获取分割结果（ModelScope返回格式：OutputKeys.TEXT）
                raw_chunks = result[OutputKeys.TEXT].strip().split("\n")

                # ============ 步骤3：后处理每个分块 ============
                cleaned_chunks = []
                for chunk in raw_chunks:
                    # 3.1 恢复文本（换行符→空格）
                    restored = self._restore_text(chunk)
                    # 3.2 二次清洗（移除分割后残留噪声）
                    final_text = self._clean_markdown(restored)
                    if final_text:  # 丢弃空块
                        cleaned_chunks.append(final_text)

                # ============ 步骤4：合并优化 ============
                merged_chunks = self.merge_chunks(cleaned_chunks)

                # ============ 步骤5：构建知识库条目 ============
                for chunk in merged_chunks:
                    knowledges.append({
                        "metadata": {
                            "source": file_path.name,  # 保留来源文件名（溯源关键）
                            "department": "",  # 预留部门字段（便于后续扩展）
                        },
                        "content": chunk,  # 清洗合并后的有效文本
                    })
                print(f"✅ 成功处理: {file_path.name} → 生成 {len(merged_chunks)} 个知识块")

            except Exception as e:
                print(f"⚠️ 处理文件 {file_path.name} 时出错: {type(e).__name__}: {e}")

        # ============ 步骤6：持久化输出 ============
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)  # 确保输出目录存在
        with open(output_path, "w", encoding="utf-8") as f:
            # ensure_ascii=False：保留中文；indent=4：美化格式便于人工检查
            json.dump(knowledges, f, ensure_ascii=False, indent=4)
        print(f"\n✨ 所有任务完成！共生成 {len(knowledges)} 个知识块")
        print(f"💾 结果已保存至: {output_file}")
        print(f"📊 知识块统计: 最小长度={min(len(k['content']) for k in knowledges)} | "
              f"最大长度={max(len(k['content']) for k in knowledges)}")


if __name__ == "__main__":
    """
    使用示例：
    1. 确保已下载ModelScope文档分割模型至 ./segmentation-models
       （推荐模型：damo/nlp_bert_document-segmentation_chinese-base）
    2. 将待处理Markdown文件放入 ./ragdatasets 目录
    3. 运行后生成 ./chunks/knowledges.json 供RAG系统使用
    """
    processor = MarkdownRAGProcessor(
        model_path="./segmentation-models",  # 可替换为ModelScope模型ID（需联网）
        min_chunk_length=120  # 根据embedding模型调整（如text2vec建议100-300）
    )
    processor.process_files(
        input_dir="./ragdatasets",
        output_file="./chunks/knowledges.json"
    )

    """
    ⚠️ 注意事项：
 	 模型要求：需提前下载文档分割模型（ModelScope支持离线加载）
    """