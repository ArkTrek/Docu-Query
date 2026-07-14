document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const statusDiv = document.getElementById('upload-status');
    const queryInput = document.getElementById('query-input');
    const sendBtn = document.getElementById('send-btn');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const activeDocIndicator = document.getElementById('active-doc-indicator');
    const clearBtn = document.getElementById('clear-btn');

    // Setup Drag and Drop
    dropZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length) handleFiles(files[0]);
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length) handleFiles(this.files[0]);
    });

    function handleFiles(file) {
        if (file.type !== 'application/pdf') {
            showStatus('Please upload a valid PDF file.', 'error');
            return;
        }

        uploadFile(file);
    }

    function showStatus(msg, type) {
        statusDiv.textContent = msg;
        statusDiv.className = `status-message status-${type}`;
    }

    function hideStatus() {
        statusDiv.className = 'status-message hidden';
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        showStatus('Uploading and processing document... This may take a moment.', 'loading');
        
        // Disable inputs during upload
        queryInput.disabled = true;
        sendBtn.disabled = true;

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showStatus('Ready!', 'success');
                activeDocIndicator.textContent = 'Document Ready';
                activeDocIndicator.classList.add('active');
                
                // Enable chat
                queryInput.disabled = false;
                sendBtn.disabled = false;
                
                // Add a system message to chat
                addMessage(`Document "${file.name}" uploaded successfully. What would you like to know?`, 'ai');
                
                setTimeout(hideStatus, 3000);
            } else {
                showStatus(data.error || 'Upload failed.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showStatus('An error occurred during upload.', 'error');
        }
        
        // Re-enable inputs if upload finishes (unless it failed, but we leave them active to try again)
        if(!document.getElementById('active-doc-indicator').classList.contains('active')) {
             queryInput.disabled = false;
             sendBtn.disabled = false;
        }
    }

    // Clear Data Functionality
    clearBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear all stored documents and chat history?')) return;

        try {
            const response = await fetch('/clear', { method: 'POST' });
            const data = await response.json();

            if (response.ok) {
                // Reset UI
                chatMessages.innerHTML = `
                    <div class="message ai-message">
                        <div class="avatar ai-avatar">AI</div>
                        <div class="message-content">
                            Hello! I am ready to answer questions. Please upload a PDF document first.
                        </div>
                    </div>
                `;
                activeDocIndicator.textContent = 'No document loaded';
                activeDocIndicator.classList.remove('active');
                queryInput.disabled = true;
                sendBtn.disabled = true;
                fileInput.value = '';
                showStatus('Data cleared successfully.', 'success');
                setTimeout(hideStatus, 3000);
            } else {
                alert('Error clearing data: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to the server to clear data.');
        }
    });

    // Chat functionality
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = queryInput.value.trim();
        if (!query) return;

        // Add user message to UI
        addMessage(query, 'user');
        queryInput.value = '';
        
        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator(typingId);

            if (response.ok) {
                addMessage(data.answer, 'ai');
            } else {
                addMessage(`Error: ${data.error}`, 'ai');
            }
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator(typingId);
            addMessage('Failed to connect to the server.', 'ai');
        }
    });

    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarStr = sender === 'user' ? 'U' : 'AI';
        
        // Convert line breaks to HTML
        let formattedContent = content;
        if (sender === 'ai') {
            formattedContent = formattedContent.replace(/\n/g, '<br>');
        }
        
        const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <div class="avatar ${sender}-avatar">${avatarStr}</div>
            <div class="message-content">
                ${formattedContent}
                <div class="message-timestamp">${timeString}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';
        messageDiv.id = id;
        
        messageDiv.innerHTML = `
            <div class="avatar ai-avatar">AI</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Simple text formatting (convert newlines to <br>)
    function formatText(text) {
        // Prevent XSS
        const div = document.createElement('div');
        div.textContent = text;
        let escaped = div.innerHTML;
        
        return escaped.replace(/\\n/g, '<br>');
    }
});
