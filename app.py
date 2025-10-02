from flask import Flask, render_template, request
from src.helper import download_hugging_face_embeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
import re

app = Flask(__name__)
load_dotenv()

# Load embeddings
embeddings = download_hugging_face_embeddings()

# Reconnect to persisted Chroma index
persist_directory = "chroma_db"
docsearch = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

# Use Mistral-7B via Ollama
chatModel = ChatOllama(model="mistral")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"].strip().lower()

    # Simple greeting check
    if re.search(r"\b(hi|hello|hey|good morning|good evening)\b", msg):
        return "Hi! How can I assist you today?"

    # Otherwise, use RAG chain for medical questions
    response = rag_chain.invoke({"input": msg})
    return str(response["answer"])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
