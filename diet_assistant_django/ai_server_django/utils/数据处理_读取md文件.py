import os
import json
import re

from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

p = pipeline(
    task=Tasks.document_segmentation,
    model="./segmentation-models",
    model_revision="master",
)

DOT_PLACEHOLDER = "__DOT__"
NEWLINE_PLACEHOLDER = "__NEWLINE__"
MIN_CHUNK_LENGTH = 120


def protect_special_chars(text):
    text = text.replace(".", DOT_PLACEHOLDER)
    text = text.replace("\n", NEWLINE_PLACEHOLDER)
    return text


def restore_special_chars(text):
    text = text.replace(DOT_PLACEHOLDER, ".")
    text = text.replace(NEWLINE_PLACEHOLDER, " ")
    return text


def clean_image_links(text):
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]\(images/.*?\)", "", text)
    return text


def normalize_spaces(text):
    return re.sub(r" +", " ", text)


def clean_table_quotes(text):
    text = re.sub(r'(\w+)="([^"]*)"', r"\1=\2", text)
    text = re.sub(r"(\w+)='([^']*)'", r"\1=\2", text)
    return text


def merge_short_chunks(chunks):
    merged_chunks = []
    accumulated_chunk = ""

    for chunk in chunks:
        if accumulated_chunk:
            accumulated_chunk += chunk
        else:
            accumulated_chunk = chunk

        if len(accumulated_chunk) >= MIN_CHUNK_LENGTH:
            merged_chunks.append(accumulated_chunk)
            accumulated_chunk = ""

    if accumulated_chunk:
        if merged_chunks:
            merged_chunks[-1] += accumulated_chunk
        else:
            merged_chunks.append(accumulated_chunk)

    return merged_chunks


if __name__ == "__main__":
    print("hello world")
    folder_path = "./ragdatasets"
    files = os.listdir(folder_path)
    knowledges = []
    for file in files:
        if file.endswith(".md"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                content = f.read()
                protected_content = protect_special_chars(content)
                result = p(documents=protected_content)
                chunks = result[OutputKeys.TEXT].strip().split("\n")

                cleaned_chunks = []
                for chunk in chunks:
                    restored_chunk = restore_special_chars(chunk)
                    cleaned_chunk = clean_image_links(restored_chunk)
                    normalized_chunk = normalize_spaces(cleaned_chunk)
                    table_cleaned_chunk = clean_table_quotes(normalized_chunk)

                    if table_cleaned_chunk.strip():
                        cleaned_chunks.append(table_cleaned_chunk)

                merged_chunks = merge_short_chunks(cleaned_chunks)

                for merged_chunk in merged_chunks:
                    knowledges.append(
                        {
                            "metadata": {
                                "source": file,
                                "department": "",
                            },
                            "content": merged_chunk.strip(),
                        }
                    )

    with open("./chunks/knowledges.json", "w", encoding="utf-8") as f:
        json.dump(knowledges, f, ensure_ascii=False, indent=4)
        print("JSON文件已写入：chunks/knowledges.json")
