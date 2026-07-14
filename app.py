import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

import shutil
from core.document_processor import process_pdf
from core.vector_store import add_documents_to_db, CHROMA_PATH, clear_db
from core.llm_chain import answer_query

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none';"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml')

# --- Model Configuration ---
LLM_MODEL = "meta/llama-3.1-70b-instruct"
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # 1. Extract text and chunk
            chunks = process_pdf(file_path)
            
            # 2. Store in Vector DB
            add_documents_to_db(chunks, embed_model_name=EMBEDDING_MODEL)
            
            # Clean up the uploaded file after processing
            os.remove(file_path)
            
            return jsonify({'message': f'Successfully processed {filename}. You can now ask questions.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

@app.route('/clear', methods=['POST'])
def clear_data():
    try:
        # Logically clear Chroma DB to avoid Windows file locks
        clear_db(EMBEDDING_MODEL)
        
        # Clear uploads folder
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
        return jsonify({'message': 'All stored data has been cleared successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400
        
    query = data['query']
    
    # 3. Retrieve and Generate answer
    try:
        response = answer_query(query, llm_model_name=LLM_MODEL, embed_model_name=EMBEDDING_MODEL)
        return jsonify({'answer': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("==================================================")
    print("Starting DocuQuery Application")
    print(f"LLM Model:       {LLM_MODEL}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print("==================================================")
    
    # Warn if API key is missing
    if not os.environ.get("NVIDIA_API_KEY"):
        print("WARNING: NVIDIA_API_KEY environment variable is not set.")
        print("Please add it to your .env file before running queries.")
    
    app.run(debug=True, port=5000)
