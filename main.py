import asyncio
from inference_pipeline import NewsPipeline


async def main():
    news_pipeline = NewsPipeline()
    print(f"Operation Sindoor.")
    async for output in news_pipeline.run_pipeline(user_request="Operation Sindoor"):
        print(output,end="",flush=True)
    print(f"Why India did Operation Sindoor?")
    async for output in news_pipeline.run_follow_up(user_request='Why India did Operation Sindoor?',task="Answer the question."):
        print(output,end="",flush=True)

if __name__ == "__main__":
    asyncio.run(main())
