from dotenv import load_dotenv
import os
from src.helper import load_pdf_file, filter_to_minimal_docs, text_split, download_hugging_face_embeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# Load documents
extracted_data = load_pdf_file(data='data/')
filter_data = filter_to_minimal_docs(extracted_data)
text_chunks = text_split(filter_data)

# Load embeddings
embeddings = download_hugging_face_embeddings()

# Create ChromaDB index (local persistence)
persist_directory = "chroma_db"

vectorstore = Chroma.from_documents(
    documents=text_chunks,
    embedding=embeddings,
    persist_directory=persist_directory
)

vectorstore.persist()
print("ChromaDB index created and persisted in:", persist_directory)
