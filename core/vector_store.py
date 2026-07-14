import os
import shutil
from langchain_chroma import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

# Directory to store the Chroma database
if os.environ.get("VERCEL") == "1":
    CHROMA_PATH = "/tmp/chroma_db"
else:
    CHROMA_PATH = os.environ.get("CHROMA_PATH", "chroma_db")

def init_vector_store(embed_model_name="nvidia/nv-embedqa-e5-v5"):
    """
    Initializes and returns a Chroma vector store instance using NVIDIA Embeddings.
    """
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable is not set.")

    embeddings = NVIDIAEmbeddings(model=embed_model_name)
    vector_store = Chroma(
        collection_name="docuquery_collection",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    return vector_store

def clear_db(embed_model_name="nvidia/nv-embedqa-e5-v5"):
    """
    Logically clears the Chroma DB by deleting the collection via the API
    rather than deleting files on disk, to prevent Windows file lock errors.
    """
    try:
        vector_store = init_vector_store(embed_model_name)
        vector_store.delete_collection()
    except Exception as e:
        # If it doesn't exist yet, it's fine
        pass

def add_documents_to_db(chunks, embed_model_name="nvidia/nv-embedqa-e5-v5"):
    """
    Adds document chunks to the Chroma vector database.
    Clears the existing database first to ensure only the latest document is queried.
    """
    # Clear existing database logically if we only want one document at a time
    clear_db(embed_model_name)
        
    vector_store = init_vector_store(embed_model_name)
    vector_store.add_documents(chunks)
    return vector_store

def get_retriever(embed_model_name="nvidia/nv-embedqa-e5-v5"):
    """
    Returns a retriever interface for the vector store.
    """
    vector_store = init_vector_store(embed_model_name)
    # Retrieve top 4 most relevant chunks
    return vector_store.as_retriever(search_kwargs={"k": 4})
