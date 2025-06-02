# app.py
import streamlit as st
import asyncio
# must be the async generator defined earlier
from inference_pipeline import run_pipeline

# ---------------------------------------------------------------------------- #
#                          Helper Wrappers & Functions                          #
# ---------------------------------------------------------------------------- #


def stream_initial_summary(topic: str):
    """
    Synchronous wrapper around the async `run_pipeline` for the initial news‐summarization.
    Yields each text chunk as soon as it arrives.
    """
    # We assume run_pipeline(topic) is an async generator yielding chunks from the model.
    return asyncio.run(run_pipeline(topic))


# async def stream_initial_summary(topic):
#     async for output in run_pipeline(topic):
#         print(output, end="", flush=True)


async def followup_pipeline_async(query: str,task:str):
    """
    If you want to add extra functionality—for example, using stored extracted_docs
    from session_state for follow‐ups—you could write a new coroutine that:
        1. Reads st.session_state["extracted_docs"] (and index/embed_model, etc.)
        2. Builds a prompt specifically for answering `query` in the context of those docs
        3. Streams chunks via model(messages=...)
    For simplicity, this example just re‐uses run_pipeline(query) and re‐fetches news;
    but you can adapt it to use the same extracted_docs instead.
    """
    async for chunk in run_pipeline(query,task=task):
        yield chunk


def stream_followup(query: str, task:str="Summarize this context"):
    """
    Synchronous wrapper around followup_pipeline_async(),
    yielding each chunk so Streamlit can display it as it arrives.
    """
    return asyncio.run(followup_pipeline_async(query,task))


# ---------------------------------------------------------------------------- #
#                            Streamlit App Layout                                #
# ---------------------------------------------------------------------------- #

st.set_page_config(page_title="News‐Summarizer Chatbot", page_icon="📰")

# Initialize session_state on first load
if "stage" not in st.session_state:
    st.session_state.stage = "input"     # can be "input" → "summarizing" → "chat"
    st.session_state.topic = ""
    # list of {"role": "user"/"assistant", "content": str}
    st.session_state.messages = []
    # (You could also store extracted_docs/index/embed_model here if you adapt follow‐ups.)
    st.session_state.summarized = False   # to track if initial summary is done


# --------------------------- PAGE: Topic Input (Stage = "input") --------------------------- #
if st.session_state.stage == "input":
    st.title("📰 News‐Summarizer Chatbot")
    st.write(
        """
        Enter a news topic (for example: “climate change,” “Operation Sindoor,” etc.).
        The app will fetch the latest news on that topic, summarize it in a streaming fashion,
        and let you ask follow‐up questions afterward.
        """
    )

    topic_input = st.text_input("Enter news topic:", key="topic_input")
    if st.button("Fetch & Summarize"):
        # Move to summarizing stage
        st.session_state.topic = topic_input.strip()
        st.session_state.stage = "summarizing"
        # Force a rerun so the summary block appears
        st.experimental_rerun()


# ---------------------- PAGE: Summarizing (Stage = "summarizing") ---------------------- #
if st.session_state.stage == "summarizing":
    st.title("📰 Summarizing News for: " + st.session_state.topic)
    placeholder = st.empty()  # This will hold the streaming summary text

    summary_text = ""  # will accumulate the streamed chunks

    # Stream the summary synchronously, but display chunk by chunk
    for chunk in stream_initial_summary(st.session_state.topic):
        # Each `chunk` is whatever the model returned (e.g. chunk.choices[0].delta["content"])
        piece = chunk.choices[0].delta.content
        summary_text += piece
        placeholder.markdown(f"**Assistant (streaming):** {summary_text}")

    # Once the loop finishes, we know the summary is done
    # Save the final assistant message and the initial user message in session_state.messages
    st.session_state.messages = [
        {"role": "user", "content": st.session_state.topic},
        {"role": "assistant", "content": summary_text},
    ]

    # Mark that summarization is complete
    st.session_state.summarized = True

    # Move to chat stage
    st.session_state.stage = "chat"

    # Force a rerun so the chat UI appears
    st.experimental_rerun()


# ------------------------ PAGE: Chat Interface (Stage = "chat") ------------------------ #
if st.session_state.stage == "chat":
    st.title(f"💬 Chat about “{st.session_state.topic}”")
    st.write(
        """
        Below is the summary of the news you requested. You can now ask follow‐up questions.
        Each response will stream as it arrives.
        """
    )

    # Display all messages so far
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])

    # A text_input (or form) for follow‐up questions
    user_question = st.text_input(
        "Ask a follow‐up question:", key="followup_input")
    if st.button("Send", key="send_followup"):
        if user_question.strip() == "":
            st.warning("Please enter a follow‐up question.")
        else:
            # 1) Append the user’s question to messages
            st.session_state.messages.append(
                {"role": "user", "content": user_question})
            # 2) Prepare a placeholder for the assistant’s streaming response
            response_placeholder = st.empty()
            answer_text = ""
            # 3) Stream the follow‐up answer chunk by chunk
            for chunk in stream_followup(user_question,task="Answer the question using the context."):
                piece = chunk.choices[0].delta.content
                answer_text += piece
                # Redisplay the entire chat, but with the assistant’s last message still streaming
                # We know it’s the last element in session_state.messages + partial answer.
                response_placeholder.markdown(
                    f"**Assistant (streaming):** {answer_text}")
            # 4) Once finished, update the final assistant reply into session_state.messages
            st.session_state.messages.append(
                {"role": "assistant", "content": answer_text})

            # Clear the follow‐up input box
            st.session_state.followup_input = ""
            # Force a rerun to show the updated chat history
            st.experimental_rerun()
