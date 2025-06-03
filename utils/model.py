from groq import Groq
from typing import List, Any
from  dotenv import load_dotenv
import os

async def get_model_response(messages: List[dict], model_id: str = "llama3-70b-8192", temperature: float = 0.2, top_p: float = 1.0, stream: bool = True) -> Any:
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    client = Groq(api_key=api_key)

    response_stream = client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )

    for chunk in response_stream:
        yield chunk



