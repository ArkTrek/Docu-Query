import os
from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_pdf(file_path):
    """
    Loads a PDF from the given file path, extracts text (using OCR if necessary via PDFPlumber),
    and chunks the text into smaller documents.
    """
    documents = []
    try:
        # First try PyPDFLoader for standard digital PDFs
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Check if text was actually extracted (could be an image-only PDF)
        extracted_text_length = sum([len(doc.page_content) for doc in documents])
        
        if extracted_text_length < 100:  # Arbitrary small threshold
            print("Low text content detected with PyPDF. Attempting with PDFPlumber for better OCR/layout extraction...")
            loader = PDFPlumberLoader(file_path)
            documents = loader.load()
            
    except Exception as e:
        print(f"Error loading PDF: {e}")
        raise e

    if not documents:
        raise ValueError("Could not extract text from the PDF.")

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    return chunks
