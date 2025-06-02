from utils.google_news import get_google_news
from utils.extract_news import download_latest_news
from utils.save_news import save_news
from utils.chunking import chunk_doc
from utils.embedding import embed_documents
from utils.encode_query import encode_query
from utils.extract_document import extract_documents
from utils.setup_prompt import get_prompt
from utils.model import get_model_response
from typing import AsyncGenerator
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def run_pipeline(user_request: str, task: str = "Summarize this context") -> AsyncGenerator[str, None]:
    logger.info(
        "Starting training pipeline for user request: '%s'", user_request)

    logger.info("Fetching news data...")
    data = get_google_news(user_request)

    logger.info("Downloading full news content...")
    data = download_latest_news(data)

    logger.info("Chunking document...")
    chunks = chunk_doc(data)

    logger.info("Embedding documents...")
    index, embed_model = embed_documents(chunks)

    logger.info("Encoding user query...")
    query_embed = encode_query(query=user_request, embedding_model=embed_model)

    logger.info("Extracting relevant documents...")
    extracted_docs = extract_documents(
        index=index, query_embedding=query_embed, all_chunks=chunks)
    print(extracted_docs)
    logger.info("Preparing prompt messages...")
    messages = get_prompt(context=extracted_docs, task=task)
    print(messages)
    logger.info("Streaming model response...")
    async for chunk in get_model_response(messages=messages):
        content = chunk.choices[0].delta.content
        if content:
            yield content
