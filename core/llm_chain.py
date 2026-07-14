import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from core.vector_store import get_retriever

def get_rag_chain(llm_model_name="meta/llama-3.1-70b-instruct", embed_model_name="nvidia/nv-embedqa-e5-v5"):
    """
    Constructs and returns the Retrieval-Augmented Generation (RAG) chain.
    """
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable is not set.")

    # Initialize the NVIDIA Chat Model
    llm = ChatNVIDIA(model=llm_model_name, temperature=0.2)

    # Define the prompt template
    template = """You are an expert Data Analysis and Extraction Specialist tasked with analyzing documents and answering questions based strictly on the provided context.
    
    When the user asks for data, metrics, or structured information:
    1. Extract the precise numbers, facts, and details from the context.
    2. Present the data clearly and logically, using Markdown tables or bulleted lists where appropriate to ensure high readability.
    3. If asked to compare or calculate basic changes based on the data in the context, do so accurately.
    
    If the answer is not contained within the context, simply state that you don't know or the data is not present in the document. Do not make up information.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    retriever = get_retriever(embed_model_name)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    # Build the chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def answer_query(query: str, llm_model_name="meta/llama-3.1-70b-instruct", embed_model_name="nvidia/nv-embedqa-e5-v5"):
    """
    Uses the RAG chain to answer a query based on the stored document.
    """
    try:
        chain = get_rag_chain(llm_model_name, embed_model_name)
        response = chain.invoke(query)
        return response
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "An error occurred while trying to answer your query. Make sure a document is uploaded and the API key is valid."
