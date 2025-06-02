import faiss
from typing import List
import numpy as np
import faiss


def extract_documents(index: faiss.Index, query_embedding: np.ndarray, all_chunks: List[str], k: int = 3) -> str:
    context = ""
    _, indices = index.search(query_embedding, k)
    for idx in indices[0]:
        context += all_chunks[idx]
    return context
