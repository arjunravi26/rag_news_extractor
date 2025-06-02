# Query example
from sentence_transformers import SentenceTransformer
import numpy as np


def encode_query(query: str, embedding_model: SentenceTransformer) -> np.ndarray:
    return embedding_model.encode([query], convert_to_numpy=True)
