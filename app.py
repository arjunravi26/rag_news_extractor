import streamlit as st
import asyncio
import time
from typing import AsyncGenerator
import logging

from inference_pipeline import NewsPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="News • AI Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apple-inspired CSS styling
st.markdown("""
<style>
    /* Import SF Pro font (Apple's system font) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Root variables - Apple color palette */
    :root {
        --apple-blue: #007AFF;
        --apple-gray: #8E8E93;
        --apple-light-gray: #F2F2F7;
        --apple-dark-gray: #1C1C1E;
        --apple-white: #FFFFFF;
        --apple-black: #000000;
        --apple-green: #34C759;
        --apple-red: #FF3B30;
        --apple-orange: #FF9500;
        --apple-purple: #AF52DE;
        --shadow-light: rgba(0, 0, 0, 0.04);
        --shadow-medium: rgba(0, 0, 0, 0.08);
        --shadow-heavy: rgba(0, 0, 0, 0.12);
    }

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Main app container - Remove extra padding/margins */
    .stApp {
        background: linear-gradient(135deg, #F5F5F7 0%, #E5E5EA 100%);
        min-height: 100vh;
        padding: 0;
        margin: 0;
        overflow-x: hidden;
    }

    /* Remove default Streamlit spacing */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
        overflow: visible !important;
    }

    /* Navigation bar */
    .nav-bar {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        padding: 1rem 0;
        position: sticky;
        top: 0;
        z-index: 1000;
        margin-bottom: 0;
    }

    .nav-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
    }

    .nav-logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--apple-black);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .nav-subtitle {
        font-size: 0.875rem;
        color: var(--apple-gray);
        font-weight: 400;
    }

    /* Hero section - Reduced padding */
    .hero {
        text-align: center;
        padding: 3rem 2rem 1.5rem;
        max-width: 900px;
        margin: 0 auto;
    }

    .hero-title {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        background: linear-gradient(135deg, var(--apple-black) 0%, var(--apple-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--apple-gray);
        font-weight: 400;
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Main input container - Centered and prominent */
    .main-input-container {
        max-width: 700px;
        margin: 0 auto;
        padding: 0 2rem 4rem;
        position: relative;
        z-index: 10;
        overflow: visible;
    }

    /* Input section styling */
    .input-section {
        background: transparent;
        border-radius: 0;
        padding: 2rem 0;
        box-shadow: none;
        border: none;
        max-width: 100%;
        margin: 0;
        position: relative;
        z-index: 15;
        overflow: visible;
    }

    /* Input label - More prominent */
    .input-label {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--apple-black);
        text-align: center;
        margin-bottom: 1.5rem;
        display: block;
        background: linear-gradient(135deg, var(--apple-black) 0%, var(--apple-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Custom input styling - Larger and more visible */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 255, 0.98) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 3px solid var(--apple-blue);
        border-radius: 20px;
        padding: 1.8rem 2rem;
        font-size: 1.2rem;
        color: var(--apple-black);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 500;
        box-shadow:
            0 12px 40px rgba(0, 122, 255, 0.2),
            0 4px 20px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        width: 100%;
        text-align: center;
        min-height: 60px;
        line-height: 1.5;
        position: relative;
        z-index: 20;
        overflow: visible;
    }

    .stTextInput > div > div > input:focus {
        background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(240, 248, 255, 1) 100%);
        border-color: var(--apple-blue);
        box-shadow:
            0 0 0 6px rgba(0, 122, 255, 0.12),
            0 16px 60px rgba(0, 122, 255, 0.25),
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 1);
        outline: none;
        transform: translateY(-2px) scale(1.01);
        z-index: 25;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--apple-gray);
        font-weight: 400;
        font-size: 1.1rem;
        text-align: center;
        opacity: 0.8;
    }

    /* Input hover state */
    .stTextInput > div > div > input:hover {
        border-color: var(--apple-blue);
        box-shadow:
            0 16px 50px rgba(0, 122, 255, 0.22),
            0 6px 25px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transform: translateY(-1px);
        background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 252, 255, 1) 100%);
        z-index: 22;
    }

    /* Button container */
    .button-container {
        display: flex;
        justify-content: center;
        margin-top: 1.5rem;
        padding: 0;
        z-index: 20;
        position: relative;
        overflow: visible;
    }

    /* Primary button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--apple-blue) 0%, #0056CC 100%);
        color: var(--apple-white);
        border: none;
        border-radius: 16px;
        padding: 1.2rem 3rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
        cursor: pointer;
        min-width: 200px;
        letter-spacing: 0.02em;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0056CC 0%, #003D99 100%);
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 122, 255, 0.4);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Secondary button */
    .secondary-btn {
        background: var(--apple-light-gray) !important;
        color: var(--apple-black) !important;
        box-shadow: none !important;
    }

    .secondary-btn:hover {
        background: #E5E5EA !important;
        transform: translateY(-1px) !important;
    }

    /* Chat interface */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 2rem;
    }

    .chat-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .chat-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--apple-black);
        margin-bottom: 0.5rem;
    }

    .chat-topic {
        background: var(--apple-blue);
        color: var(--apple-white);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
    }

    /* Message styling */
    .message {
        margin: 1.5rem 0;
        animation: fadeInUp 0.3s ease;
    }

    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
    }

    .user-message .message-content {
        background: var(--apple-blue);
        color: var(--apple-white);
        padding: 1rem 1.25rem;
        border-radius: 20px 20px 4px 20px;
        max-width: 70%;
        font-weight: 400;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
    }

    .bot-message {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 1rem;
    }

    .bot-message .message-content {
        background: var(--apple-white);
        color: var(--apple-black);
        padding: 1.5rem;
        border-radius: 20px 20px 20px 4px;
        max-width: 80%;
        box-shadow: 0 2px 12px var(--shadow-light);
        border: 1px solid rgba(0, 0, 0, 0.04);
        line-height: 1.6;
    }

    /* Loading animation */
    .loading-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }

    .loading-dots {
        display: flex;
        gap: 0.5rem;
    }

    .loading-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--apple-blue);
        animation: pulse 1.4s ease-in-out infinite both;
    }

    .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dot:nth-child(2) { animation-delay: -0.16s; }
    .loading-dot:nth-child(3) { animation-delay: 0s; }

    @keyframes pulse {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .nav-content {
            padding: 0 1rem;
        }

        .hero {
            padding: 2rem 1rem 1rem;
        }

        .main-input-container {
            padding: 0 1rem 2rem;
        }

        .chat-container {
            padding: 0 1rem;
        }

        .user-message .message-content,
        .bot-message .message-content {
            max-width: 90%;
        }

        .hero-title {
            font-size: clamp(2rem, 8vw, 3rem);
        }

        .hero-subtitle {
            font-size: 1.1rem;
        }

        .stTextInput > div > div > input {
            padding: 1.5rem;
            font-size: 1.1rem;
        }

        .stButton > button {
            padding: 1rem 2.5rem;
            font-size: 1rem;
            min-width: 180px;
        }
    }

    /* Accessibility improvements */
    .stButton > button:focus {
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.3);
        outline: none;
    }

    .stTextInput > div > div > input:focus {
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
    }

    /* Error and success states */
    .stError {
        background: rgba(255, 59, 48, 0.1);
        border: 1px solid var(--apple-red);
        border-radius: 12px;
        color: var(--apple-red);
        margin: 1rem 0;
    }

    .stSuccess {
        background: rgba(52, 199, 89, 0.1);
        border: 1px solid var(--apple-green);
        border-radius: 12px;
        color: var(--apple-green);
        margin: 1rem 0;
    }

    /* Remove extra spacing from Streamlit elements */
    .element-container {
        margin: 0 !important;
        overflow: visible !important;
    }

    /* Input container specific styling */
    .stTextInput {
        margin-bottom: 0 !important;
        overflow: visible !important;
        position: relative;
        z-index: 20;
    }

    .stTextInput > label {
        display: none !important;
    }

    /* Ensure all input-related containers are visible */
    .stTextInput > div {
        overflow: visible !important;
        position: relative;
        z-index: 20;
    }

    .stTextInput > div > div {
        overflow: visible !important;
        position: relative;
        z-index: 20;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'news_topic' not in st.session_state:
        st.session_state.news_topic = ''
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'summary_generated' not in st.session_state:
        st.session_state.summary_generated = False
    if 'current_summary' not in st.session_state:
        st.session_state.current_summary = ''
    if 'news_pipeline' not in st.session_state:
        st.session_state.news_pipeline = NewsPipeline()

def render_navigation():
    """Render Apple-style navigation bar"""
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-content">
            <div class="nav-logo">
                📰 News
                <div class="nav-subtitle">AI Summarizer</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_home_page():
    """Display the home page with Apple-inspired design"""
    render_navigation()

    # Hero section - more compact
    st.markdown("""
    <div class="hero">
        <h1 class="hero-title">Stay Informed.<br>Stay Ahead.</h1>
        <p class="hero-subtitle">
            Get AI-powered summaries of the latest news, tailored to your interests.
            Ask questions, dive deeper, and understand what matters most.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Input section - better positioned and sized
    st.markdown('<div class="main-input-container">', unsafe_allow_html=True)
    st.markdown('<div class="input-section">', unsafe_allow_html=True)

    # Input label
    st.markdown('<div class="input-label">What news interests you today?</div>', unsafe_allow_html=True)

    # Input field
    news_topic = st.text_input(
        "",
        placeholder="Enter any topic: technology, politics, sports, health...",
        key="news_input",
        label_visibility="collapsed"
    )

    # Button with better positioning
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("Get News Summary", key="submit_btn"):
        if news_topic.strip():
            st.session_state.news_topic = news_topic.strip()
            st.session_state.page = 'chat'
            st.rerun()
        else:
            st.error("Please enter a news topic to get started.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close input-section
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-input-container

async def generate_summary():
    """Generate initial news summary with streaming"""
    try:
        # Create message container
        with st.container():
            st.markdown('<div class="message bot-message">', unsafe_allow_html=True)
            st.markdown('<div class="message-content">', unsafe_allow_html=True)

            text_placeholder = st.empty()
            current_text = ""

            news_pipeline = st.session_state.news_pipeline
            async for chunk in news_pipeline.run_pipeline(
                st.session_state.news_topic,
                "Provide a comprehensive summary of the latest news"
            ):
                current_text += chunk
                text_placeholder.markdown(current_text + "▊")
                await asyncio.sleep(0.01)

            text_placeholder.markdown(current_text)
            st.markdown('</div></div>', unsafe_allow_html=True)

        st.session_state.current_summary = current_text
        st.session_state.summary_generated = True
        return current_text

    except Exception as e:
        st.error(f"Unable to generate summary: {str(e)}")
        logger.error(f"Summary generation error: {e}")
        return None
async def generate_response(user_question: str, response_placeholder):
    """Generate response to user question with streaming in the provided placeholder"""
    try:
        current_text = ""
        news_pipeline = st.session_state.news_pipeline

        async for chunk in news_pipeline.run_follow_up(
            user_request=user_question,
            task=f"Answer this question based on the news about {st.session_state.news_topic}"
        ):
            current_text += chunk
            # Update the placeholder with typing cursor effect
            response_placeholder.markdown(f"""
            <div class="message bot-message">
                <div class="message-content">{current_text}▊</div>
            </div>
            """, unsafe_allow_html=True)
            await asyncio.sleep(0.01)

        # Final update without cursor
        response_placeholder.markdown(f"""
        <div class="message bot-message">
            <div class="message-content">{current_text}</div>
        </div>
        """, unsafe_allow_html=True)

        return current_text

    except Exception as e:
        error_msg = "I apologize, but I encountered an error while processing your question. Please try again."
        response_placeholder.markdown(f"""
        <div class="message bot-message">
            <div class="message-content" style="color: var(--apple-red);">{error_msg}</div>
        </div>
        """, unsafe_allow_html=True)
        logger.error(f"Response generation error: {e}")
        return error_msg

    except Exception as e:
        error_msg = "I apologize, but I encountered an error while processing your question. Please try again."
        response_placeholder.markdown(f"""
        <div class="message bot-message">
            <div class="message-content" style="color: var(--apple-red);">{error_msg}</div>
        </div>
        """, unsafe_allow_html=True)
        logger.error(f"Response generation error: {e}")
        return error_msg


def display_chat_page():
    """Display the chat interface"""
    render_navigation()

    # Chat header
    st.markdown(f"""
    <div class="chat-header">
        <h1 class="chat-title">News Summary</h1>
        <span class="chat-topic">{st.session_state.news_topic}</span>
    </div>
    """, unsafe_allow_html=True)

    # Back button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← New Search", key="back_btn"):
            st.session_state.page = 'home'
            st.session_state.summary_generated = False
            st.session_state.chat_history = []
            st.session_state.current_summary = ''
            st.rerun()

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Generate initial summary if not done
    if not st.session_state.summary_generated:
        st.markdown("""
        <div class="loading-container">
            <div class="loading-dots">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Analyzing latest news articles...**")

        summary = asyncio.run(generate_summary())
        if summary:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": summary
            })
    else:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message user-message">
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message bot-message">
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # User input section
    if st.session_state.summary_generated:
        st.markdown("---")

        user_question = st.text_input(
            "",
            placeholder="Ask a follow-up question about this news topic...",
            key="user_question",
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Send", key="send_question"):
                if user_question.strip():
                    # Add user question to chat history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_question
                    })

                    # Generate and add response
                    response_placeholder = st.empty()
                    response = asyncio.run(generate_response(user_question,response_placeholder))
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                    st.rerun()

def main():
    """Main application entry point"""
    initialize_session_state()

    if st.session_state.page == 'home':
        display_home_page()
    elif st.session_state.page == 'chat':
        display_chat_page()

if __name__ == "__main__":
    main()