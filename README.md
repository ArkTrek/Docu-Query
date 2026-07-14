# DocuQuery

DocuQuery is a modern, AI-powered Flask web application that allows you to upload PDF documents and ask questions about their content using NVIDIA's powerful Large Language Models (LLMs) via LangChain. 

## 🚀 Features

- **Flask Backend:** A fast, local Flask application managing the web interface, API routes, and data pipelines.
- **Advanced PDF Processing:** Extracts text using `PyPDFLoader` and falls back to OCR via `pdfplumber` for image-heavy documents. 
- **Vector Search & RAG:** Automatically chunks text and stores it locally in a Chroma vector database. It uses Retrieval-Augmented Generation (RAG) to provide accurate answers based *only* on your uploaded document.
- **AI Models Used:** 
  - **LLM:** `meta/llama-3.1-70b-instruct` for intelligent reasoning and query answering.
  - **Embeddings:** `nvidia/nv-embedqa-e5-v5` for high-quality semantic vector representations.
- **Security First:** 
  - API keys are managed securely via `.env` files and should never be committed to GitHub.
  - Uploaded files are automatically and immediately deleted from the server after they are processed into the vector database.
- **Documentation Ready:** Built-in `/docs` route available for project documentation.

## 📋 Prerequisites

- **Python:** Version 3.10
- **NVIDIA API Key:** Required for the models (Get one from [build.nvidia.com](https://build.nvidia.com/)).
- ***(Optional)* Tesseract-OCR:** For OCR fallback on Windows, installed and added to your system PATH.

## 🛠️ Setup

1. **Configure Environment**
   Create a `.env` file in the root directory and add your NVIDIA API key. This file keeps your credentials secure.
   ```env
   NVIDIA_API_KEY=nvapi-your-key-here
   ```

## 💻 Usage

### Option 1: Quick Start (Windows)
We provide a convenient `runner.bat` script that automatically creates a virtual environment, installs all dependencies, and starts the server.
1. Run the script from your terminal or double-click it:
   ```cmd
   .\runner.bat
   ```

### Option 2: Manual Setup
1. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application:**
   ```bash
   python app.py
   ```

### Using the App
1. Once running, open `http://127.0.0.1:5000` in your web browser.
2. Drag and drop a PDF file into the designated upload zone.
3. Wait for the processing to complete. The original file is removed instantly for your security.
4. Use the chat interface to query information directly from your uploaded document!

## 🔒 Security Best Practices
- Ensure your `.env` file is included in your `.gitignore`.
- Your vector data remains on your local machine within the `chroma_db` folder.
- The `uploads` directory is routinely purged to prevent sensitive data accumulation.
