# 🎥 YouTube Video Summarizer & Q&A

## Recruiter quick view

**Problem:** Finding answers within a long YouTube video can require searching an entire transcript.

**Approach:** Retrieve available video transcripts, split them into chunks, create embeddings, index them in Chroma and use retrieval-augmented generation to answer questions.

**Architecture:** YouTube transcript → chunking → embeddings → vector index → relevant context retrieval → LLM response → Flask API.

**Current scope:** Transcript-based question answering. A dedicated automatic summary endpoint and polished interactive frontend are **not yet implemented**, as noted below.

**Limitations to test:** Videos without accessible transcripts, multilingual transcripts, long-video processing, embedding quality and unsupported claims in generated answers.


<p align="center">
  <strong>Turn YouTube video transcripts into searchable knowledge using Retrieval-Augmented Generation (RAG) and Large Language Models.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge" alt="LangChain"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Database-2E8B57?style=for-the-badge" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/Hugging%20Face-LLM%20Integration-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="Hugging Face"/>
</p>

## 📌 Overview

**YouTube Video Summarizer & Q&A** is a Python-based application that uses AI to make YouTube video content easier to explore and understand.

The project implements a **Retrieval-Augmented Generation (RAG)** pipeline that retrieves a video's transcript, divides it into smaller text chunks, converts the chunks into embeddings, and stores them in a Chroma vector database.

When a question is submitted, the system retrieves relevant transcript sections and passes them to a language model to generate a context-grounded answer.

A Flask REST API provides an endpoint for submitting questions and receiving answers in JSON format.

> **Current implementation:** The application currently supports transcript-based question answering. A dedicated video-summary endpoint and interactive frontend are potential future enhancements.

## ✨ Key Features

- 🎬 **YouTube Transcript Extraction:** Retrieves transcript text using `youtube-transcript-api`.
- ✂️ **Intelligent Text Chunking:** Splits transcript text into smaller sections with overlapping context.
- 🧠 **Text Embeddings:** Uses Hugging Face embeddings for semantic representation.
- 🗄️ **Vector Database:** Stores transcript chunks and embeddings in ChromaDB.
- 🔎 **Semantic Retrieval:** Uses Maximum Marginal Relevance (MMR) to retrieve relevant transcript passages.
- 🤖 **LLM Integration:** Uses Llama 3.1 8B Instruct through the Hugging Face endpoint integration.
- 🔗 **RAG Pipeline:** Connects document retrieval, prompt construction, language-model inference, and output parsing.
- 🌐 **Flask REST API:** Exposes a `/ask` endpoint for question answering.
- 📚 **Context-Grounded Responses:** Instructs the language model to answer using the retrieved transcript context.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Flask | REST API development |
| YouTube Transcript API | Transcript extraction |
| LangChain | RAG pipeline orchestration |
| ChromaDB | Vector storage and retrieval |
| Hugging Face Embeddings | Text embedding generation |
| Hugging Face Endpoint | Language-model inference |
| Llama 3.1 8B Instruct | Question-answer generation |
| python-dotenv | Environment variable management |

## 🏗️ System Architecture

The application follows a retrieval-augmented question-answering workflow.

1. **Transcript Extraction:** Fetches the transcript of the configured YouTube video.
2. **Text Preprocessing:** Splits the transcript into chunks of approximately 1,000 characters with 200 characters of overlap.
3. **Embedding Generation:** Converts the transcript chunks into vector embeddings.
4. **Vector Storage:** Stores the embedded documents in ChromaDB.
5. **Context Retrieval:** Retrieves up to five relevant chunks using MMR-based retrieval.
6. **Prompt Construction:** Combines retrieved context with the user's question.
7. **Answer Generation:** Sends the prompt to the configured Llama model.
8. **API Response:** Returns the generated answer as JSON through Flask.

## 🔄 RAG Workflow

```text
YouTube Video
      |
      v
Transcript Extraction
      |
      v
Text Chunking
      |
      v
Hugging Face Embeddings
      |
      v
ChromaDB Vector Store
      |
      v
User Question
      |
      v
Semantic Retrieval (MMR)
      |
      v
Retrieved Context + Question
      |
      v
Llama 3.1 via Hugging Face
      |
      v
Answer Returned by Flask API
```

## 📂 Project Structure

```text
YT-Video-summarizer/
│
├── README.md
│
└── YT_bot/
    ├── ragbot.py
    └── requirements_ragbot.txt
```

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10 or later recommended
- Git
- pip
- A Hugging Face access token with access to the configured model endpoint

### Step 1: Clone the repository

```bash
git clone https://github.com/sumitgole011/YT-Video-summarizer.git
cd YT-Video-summarizer
```

### Step 2: Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r YT_bot/requirements_ragbot.txt
```

### Step 4: Configure your Hugging Face token

Create a `.env` file in the project root:

```env
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

Replace the placeholder with your own token and verify that it is recognized by the installed Hugging Face integration.

**Security:** Never upload your actual API token or other credentials to GitHub.

### Step 5: Configure the YouTube video

Open `YT_bot/ragbot.py` and update the video ID configured in the source:

```python
video_id = "YOUR_YOUTUBE_VIDEO_ID"
```

Use a video with an accessible transcript. The current implementation configures the video ID directly in the source code rather than receiving it dynamically through an API request.

### Step 6: Run the application

From the repository root, execute:

```bash
python YT_bot/ragbot.py
```

The Flask API starts on port `5000`.

## 🔌 API Documentation

### Ask a question about the video

**Endpoint:** `/ask`

**Method:** `POST`

**Local URL:** `http://127.0.0.1:5000/ask`

**Request headers:**

```http
Content-Type: application/json
```

**Request body:**

```json
{
  "question": "What are the main concepts explained in this video?"
}
```

**Example using cURL:**

```bash
curl -X POST http://127.0.0.1:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the main concepts explained in this video?"}'
```

**Example response:**

```json
{
  "answer": "The generated answer based on the retrieved transcript context."
}
```

The response shown above illustrates the JSON structure; the actual answer depends on the selected video's transcript and the retrieved passages.

### Input validation and runtime notes

The `/ask` endpoint expects a JSON object with a non-empty string `question`. Missing or invalid payloads return HTTP 400. The Flask development server runs with debugging disabled; **do not use it as a production WSGI server**. The transcript and embeddings are initialized on startup, so failures in transcript availability, package compatibility, or model credentials can prevent the API from starting. These changes have not been validated by a live end-to-end run.

## 🧠 Key Concepts Demonstrated

- Retrieval-Augmented Generation (RAG)
- Semantic search and document retrieval
- Text embeddings and vector databases
- Recursive text splitting and overlapping chunks
- Maximum Marginal Relevance (MMR)
- LangChain runnable pipelines
- Large Language Model integration
- Flask API development
- Environment-based configuration

## 🔮 Future Enhancements

- Accept YouTube URLs or video IDs directly through the API.
- Add a dedicated endpoint for generating concise video summaries.
- Develop a Streamlit or web-based chat interface.
- Cache transcript embeddings to reduce repeated processing.
- Add transcript citations and timestamps to answers.
- Implement validation and error handling for unavailable transcripts.
- Add automated testing, logging, and deployment documentation.

## ⚠️ Current Limitations

- The YouTube video ID is configured in the source code.
- The transcript must be accessible through the transcript service.
- The vector store is built when the application initializes, which can increase startup time.
- The current API provides question answering rather than a separate summarization endpoint.
- Answers depend on retrieved context and should be verified when accuracy is important.

## 👨‍💻 Author

**Sumit Gole**

- GitHub: [@sumitgole011](https://github.com/sumitgole011)
- Repository: [YT-Video-summarizer](https://github.com/sumitgole011/YT-Video-summarizer)

---

<p align="center">
  <strong>Making video knowledge more accessible with AI, semantic retrieval, and language models.</strong>
</p>
