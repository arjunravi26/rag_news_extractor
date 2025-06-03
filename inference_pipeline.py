import logging
from typing import AsyncGenerator

from utils.news_fetcher import get_google_news
from utils.scraper import download_latest_news
from utils.save_news import save_news
from utils.chunking import chunk_doc
from utils.embedding import embed_documents
from utils.encode_query import encode_query
from utils.extract_document import extract_documents
from utils.setup_prompt import get_prompt
from utils.model import get_model_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NewsPipeline:
    def __init__(self):
        self.index = None
        self.embed_model = None
        self.chunks = []

    async def run_pipeline(
        self, user_request: str, task: str = "Summarize this context"
    ) -> AsyncGenerator[str, None]:
        """
        Fetches news based on the user_request, processes and embeds chunks,
        and then streams a model response (e.g., summary or answer).

        After this method completes, self.index, self.embed_model, and self.chunks
        are populated, so they can be re-used in run_follow_up.
        """
        logger.info("Starting training pipeline for user request: '%s'", user_request)

        logger.info("Fetching news data...")
        data = get_google_news(user_request)

        logger.info("Downloading full news content...")
        data = download_latest_news(data)

        logger.info("Chunking document...")
        self.chunks = chunk_doc(data)

        logger.info("Embedding documents...")
        self.index, self.embed_model = embed_documents(self.chunks)

        logger.info("Encoding user query...")
        query_embed = encode_query(query=user_request, embedding_model=self.embed_model)

        logger.info("Extracting relevant documents...")
        extracted_docs = extract_documents(
            index=self.index, query_embedding=query_embed, all_chunks=self.chunks
        )

        logger.info("Preparing prompt messages...")
        messages = get_prompt(context=extracted_docs, task=task)

        logger.info("Streaming model response...")
        async for chunk in get_model_response(messages=messages):
            content = chunk.choices[0].delta.content
            if content:
                yield content

    async def run_follow_up(
        self, user_request: str, task: str = "Summarize this context"
    ) -> AsyncGenerator[str, None]:
        """
        Uses the already-computed index, embed_model, and chunks from run_pipeline
        to process a follow-up query and stream a model response.
        """
        if self.index is None or self.embed_model is None or not self.chunks:
            raise RuntimeError(
                "Pipeline has not been initialized. "
                "Please call run_pipeline(...) before run_follow_up(...)."
            )

        logger.info("Encoding user query for follow-up: '%s'", user_request)
        query_embed = encode_query(query=user_request, embedding_model=self.embed_model)

        logger.info("Extracting relevant documents (follow-up)...")
        extracted_docs = extract_documents(
            index=self.index, query_embedding=query_embed, all_chunks=self.chunks
        )

        logger.info("Preparing prompt messages (follow-up)...")
        messages = get_prompt(context=extracted_docs, task=task)

        logger.info("Streaming model response (follow-up)...")
        async for chunk in get_model_response(messages=messages):
            content = chunk.choices[0].delta.content
            if content:
                yield content
