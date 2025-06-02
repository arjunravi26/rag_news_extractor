from langchain.schema import SystemMessage, HumanMessage

def get_prompt(context: str, task: str):

    SYSTEM_PROMPT = """
    You are an expert news curator and writer. Based solely on the provided context, perform the specified task (e.g., summarization or question answering).
    Do not include any information not present in the context.
    Write in an engaging, user-friendly news style: start with a clear, concise title, then present the content in short, factual paragraphs, maintaining a curious and informative tone.
    Use factual language, avoid opinions, and maintain objectivity. Ensure clarity and cohesion throughout.
    """.strip()

    system_msg_obj = SystemMessage(content=SYSTEM_PROMPT)
    human_msg_obj = HumanMessage(
        content=(
            "Here is the context—do not hallucinate.\n"
            f"context: {context}\n"
            f"task: {task}"
        )
    )

    messages = [
        {"role": "system", "content": system_msg_obj.content},
        {"role": "user",   "content": human_msg_obj.content},
    ]
    return messages
