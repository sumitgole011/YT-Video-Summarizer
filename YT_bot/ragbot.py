from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.runnables import RunnableParallel , RunnableLambda , RunnablePassthrough
from dotenv import load_dotenv

# ------------------------------
# Setup
# ------------------------------
video_id = "F0GQ0l2NfHA"
ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch(video_id)
full_text = " ".join([entry.text for entry in transcript])

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents(splitter.split_text(full_text))

embedding_model = HuggingFaceEmbeddings()
vector_store = Chroma.from_documents(
    embedding=embedding_model,
    documents=chunks
)

retriever = vector_store.as_retriever(search_type='mmr', kwargs={'k': 5})

template = PromptTemplate(
     template="""You are a helpful assistant.
                Answer ONLY from the provided transcript context.
                If the context is insufficient, just say you don't know.

                {context}
                Question: {question}
                """,
    input_variables=['context','question']
)

load_dotenv()
llm = HuggingFaceEndpoint(repo_id="meta-llama/Llama-3.1-8B-Instruct", task='text-generation')
model = ChatHuggingFace(llm=llm)

def chunk_merge(docs):
    return '\n\n'.join([i.page_content for i in docs])

parallel = RunnableParallel({
    'context': retriever | RunnableLambda(chunk_merge),
    'question': RunnablePassthrough()
})

parse = StrOutputParser()
chain = parallel | template | model | parse

# ------------------------------
# Flask API
# ------------------------------
app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    answer = chain.invoke(question.strip())
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(port=5000, debug=False)
