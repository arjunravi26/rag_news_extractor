# RAG News Extractor

A Retrieval-Augmented Generation (RAG) system that extracts, ingests, and serves relevant news content from Google News. Leveraging web scraping, text chunking, embedding, and a vector database, this project allows users to ask about any news topic, receive a summarized overview, and follow up with streaming answers.

## Table of Contents

- [Features](#features)
- [Architecture & Workflow](#architecture--workflow)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Automated News Extraction**
  • Query Google News for a given topic
  • Scrape individual news articles using Beautiful Soup

- **Document Processing & Chunking**
  • Clean and normalize raw HTML content
  • Chunk documents using LangChain’s `RecursiveCharacterTextSplitter`

- **Dense Embedding & Vector Storage**
  • Embed each text chunk with Sentence-Transformers
  • Store embeddings in a FAISS vector database for fast retrieval

- **Retrieval & Summarization**
  • On user query, retrieve the top-k relevant chunks from FAISS
  • Summarize retrieved chunks via Groq LLaMA model (streaming output)

- **Follow-Up Questions**
  • Maintain context to answer follow-up queries about the same news topic
  • Stream responses as the model generates them

- **Web Interface (Streamlit)**
  • Simple, interactive UI to enter topics and view summaries
  • Real-time, streaming answer display

## Architecture & Workflow

1. **User Input**
   - User enters a news topic in the Streamlit UI.

2. **News Retrieval**
   1. Query Google News for top headlines/links matching the topic.
   2. For each news link, scrape the article text using Beautiful Soup.
   3. Store raw text locally (optional cache).

3. **Text Chunking**
   - Use LangChain’s `RecursiveCharacterTextSplitter` to split each article into manageable chunks (e.g., 1,000 tokens each, with overlap).

4. **Embedding & Indexing**
   1. For each text chunk, compute a dense embedding via a Sentence-Transformer model (e.g., `all-MiniLM-L6-v2`).
   2. Insert embeddings into a FAISS index, along with metadata (source URL, chunk ID).

5. **Querying & Summarization**
   1. When the user asks “Summarize the latest news on [topic]”:
      - Embed the user question.
      - Retrieve the top-k closest chunks from FAISS.
      - Concatenate/re-rank retrieved chunks as needed.
      - Stream the summarization from Groq LLaMA (prompted via LangChain).
   2. For follow-up questions:
      - Context window includes system prompt + retrieved chunks.
      - Generate a streaming reply via the same Groq LLaMA pipeline.

6. **Streamlit Frontend**
   - Displays:
     • A text input for “Enter a news topic”
     • A “Submit” button to trigger the RAG pipeline
     • A live, streaming text area to show the LLaMA-generated summary/answer

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/arjunravi26/rag_news_extractor.git
   cd rag_news_extractor

2. **Create a Python virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate       # On Windows: .venv\Scripts\activate
   ```

3. **Install required packages**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (if applicable)

   * If your project requires API keys (e.g., custom Google News API, LLaMA credentials), create a `.env` file in the root directory:

     ```dotenv
     GROQ_API_KEY=your_openai_api_key_here
     ```
   * Ensure that `.env` is listed in `.gitignore` to avoid committing secrets.

5. **Initialize FAISS Index**
   
   * If starting fresh, the first run of the Streamlit app will build the FAISS database from scratch.

## Usage

1. **Run the Streamlit App**

   ```bash
   streamlit run app.py
   ```

   * A browser window/tab will open at `http://localhost:8501/`.
   * Enter a news topic (e.g., “Artificial Intelligence”) and click **Submit**.

2. **Interact with the System**

   * The app will display a streaming summary of the latest news related to your topic.
   * After the initial summary, you can enter follow-up questions in a text box (e.g., “What are the main challenges?”).
   * The answer will stream in real time, leveraging the existing context window + retrieved chunks.


## Dependencies

* **Core Libraries**

  * [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) — Web scraping
  * [LangChain](https://github.com/langchain-ai/langchain) — Text splitting & prompt templates
  * [Sentence Transformers](https://www.sbert.net/) — Dense text embeddings
  * [FAISS](https://github.com/facebookresearch/faiss) — Vector database
  * [Groq LLaMA](https://github.com/groq/groq-llama) — LLM for summarization & Q\&A
  * [Streamlit](https://streamlit.io/) — Web interface


* **Python Version**

  * Tested with Python 3.9+. Higher versions may work but ensure compatibility with FAISS and Sentence-Transformers.

Install everything via:

```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! If you’d like to:

1. **Report a Bug**
   • Open an issue and provide a clear description of the problem and steps to reproduce.

2. **Request a Feature**
   • Open an issue labeled “enhancement” explaining the feature goal and use case.

3. **Submit a Pull Request**

   1. Fork the repository.
   2. Create a new branch:

      ```bash
      git checkout -b feature/your-feature-name
      ```
   3. Make sure to update tests (if any) and add documentation if your change affects the user interface or CLI.
   4. Run a quick formatting check (e.g., `flake8` or `black`).
   5. Submit a pull request against the `main` branch.

Thank you for helping improve this project!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Built by [arjunravi26](https://github.com/arjunravi26)*

```
