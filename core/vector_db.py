import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

FAISS_INDEX_PATH = os.getenv("VECTOR_DB_PATH", "faiss_index")

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def build_index(chunks):
    """Build a FAISS vector database from document chunks."""
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"FAISS index built and saved to {FAISS_INDEX_PATH}")
    return vectorstore

def load_index():
    """Load the FAISS index if it exists."""
    if os.path.exists(FAISS_INDEX_PATH):
        embeddings = get_embeddings()
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return None
