from sentence_transformers import SentenceTransformer
from typing import List,Tuple
import faiss


def embed_documents(all_chunks: List) -> Tuple[faiss.Index,SentenceTransformer]:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight & fast
    corpus_embeddings = embedding_model.encode(all_chunks, convert_to_numpy=True)
    embedding_dimension = corpus_embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dimension)  # L2 = Euclidean distance
    index.add(corpus_embeddings)
    return index,embedding_model
