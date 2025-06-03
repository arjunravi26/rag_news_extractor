from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import os


def chunk_doc(documents: List):
    # documents = []
    # for filename in os.listdir(file_path):
    #     if filename.endswith(".txt"):
    #         with open(os.path.join(file_path, filename), 'r', encoding='utf-8') as file:
    #             documents.append(file.read())
    # Aim for ~350–450 token chunks ≃ 1 400–1 800 characters each.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1600,    # ≃ 400 tokens × 4 chars/token
        chunk_overlap=200   # ≃ 20% overlap (200 chars ≃ 50 tokens)
    )

    all_chunks = []
    for doc in documents['description']:
        chunks = text_splitter.split_text(doc)
        all_chunks.extend(chunks)

    return all_chunks