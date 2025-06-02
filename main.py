import asyncio
from inference_pipeline import run_pipeline

async def main():
    async for output in run_pipeline("Operation Sindoor"):
        print(output, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())