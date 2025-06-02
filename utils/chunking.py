from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import os


def chunk_doc(documents: List):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    # documents = []
    # for filename in os.listdir(file_path):
    #     if filename.endswith(".txt"):
    #         with open(os.path.join(file_path, filename), 'r', encoding='utf-8') as file:
    #             documents.append(file.read())

    all_chunks = []
    for doc in documents['description']:
        chunks = text_splitter.split_text(doc)
        all_chunks.extend(chunks)
    print(chunks)
    return all_chunks
