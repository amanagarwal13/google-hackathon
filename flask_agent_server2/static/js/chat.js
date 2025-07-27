/**
 * ADK Agent Chat Interface JavaScript
 */

// Global variables
let socket = null;
let isConnected = false;
let currentTheme = localStorage.getItem('theme') || 'light';

// Initialize chat application
function initializeChat() {
    // Apply saved theme
    applyTheme(currentTheme);
    
    // Initialize Socket.IO connection
    initializeSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    // Setup file upload
    setupFileUpload();
    
    // Update timestamps for any template messages
    updateTemplateTimestamps();
    
    // Focus on input
    document.getElementById('messageInput').focus();
}

// Update timestamps for messages that don't have them (from template)
function updateTemplateTimestamps() {
    const emptyTimestamps = document.querySelectorAll('.message-time:empty');
    const currentTime = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    
    emptyTimestamps.forEach(timeSpan => {
        timeSpan.textContent = currentTime;
    });
}

// Initialize Socket.IO connection
function initializeSocket() {
    socket = io({
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
    });
    
    // Connection events
    socket.on('connect', () => {
        console.log('Connected to server');
        isConnected = true;
        updateConnectionStatus(true);
        
        // Join session with agent name
        socket.emit('join_session', { 
            session_id: SESSION_ID,
            agent_name: AGENT_NAME 
        });
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        isConnected = false;
        updateConnectionStatus(false);
    });
    
    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        updateConnectionStatus(false);
    });
    
    // Chat events
    socket.on('joined', (data) => {
        console.log('Joined session:', data.session_id, 'Agent:', data.agent_name);
    });
    
    socket.on('session_history', (data) => {
        // Load session history
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                if (msg.role === 'user') {
                    addMessage(msg.content, 'user', msg.timestamp);
                } else {
                    addMessage(msg.content, 'assistant', msg.timestamp);
                }
            });
        }
    });
    
    socket.on('agent_response', (data) => {
        addMessage(data.response, 'assistant', data.timestamp);
        hideTypingIndicator();
    });
    
    socket.on('agent_typing', (data) => {
        if (data.typing) {
            showTypingIndicator();
        } else {
            hideTypingIndicator();
        }
    });
    
    socket.on('agent_error', (data) => {
        addMessage(`Error: ${data.error}`, 'error');
        hideTypingIndicator();
    });
    
    socket.on('agent_info', (data) => {
        updateAgentInfo(data);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Send button
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    
    // Clear session
    document.getElementById('clearSession').addEventListener('click', clearSession);
    
    // New chat
    document.getElementById('newChat').addEventListener('click', newChat);
    
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Download chat
    document.getElementById('downloadChat').addEventListener('click', downloadChat);
    
    // Sidebar toggle
    document.getElementById('toggleSidebar').addEventListener('click', toggleSidebar);
    document.getElementById('mobileMenu').addEventListener('click', toggleSidebar);
    
    // Character count
    document.getElementById('messageInput').addEventListener('input', updateCharCount);
    
    // File attachment
    document.getElementById('attachFile').addEventListener('click', () => {
        document.getElementById('fileModal').style.display = 'flex';
    });
}

// Send message
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    updateCharCount();
    
    // Send via Socket.IO or fallback to REST API
    if (isConnected && socket) {
        socket.emit('chat_message', {
            message: message,
            session_id: SESSION_ID,
            app_name: AGENT_NAME
        });
    } else {
        sendViaAPI(message);
    }
}

// Send message via REST API (fallback)
async function sendViaAPI(message) {
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID,
                app_name: AGENT_NAME
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessage(data.response, 'assistant');
        } else {
            addMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addMessage(`Connection error: ${error.message}`, 'error');
    } finally {
        hideTypingIndicator();
    }
}

// Add message to chat
function addMessage(content, type, timestamp = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const time = timestamp ? new Date(timestamp) : new Date();
    const timeString = time.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
    });
    
    const avatarIcon = type === 'user' ? 'fa-user' : (window.AGENT_INFO?.icon || 'fa-robot');
    const author = type === 'user' ? 'You' : 'Agent';
    
    // Parse markdown content
    const parsedContent = type === 'assistant' ? marked.parse(content) : escapeHtml(content);
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">${author}</span>
                <span class="message-time">${timeString}</span>
            </div>
            <div class="message-body">
                ${parsedContent}
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    
    // Highlight code blocks
    messageDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    // Scroll to bottom
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'flex';
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'none';
}

// Scroll to bottom of chat
function scrollToBottom() {
    const container = document.getElementById('chatContainer');
    container.scrollTop = container.scrollHeight;
}

// Handle key down in input
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Auto resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// Update character count
function updateCharCount() {
    const input = document.getElementById('messageInput');
    const charCount = document.getElementById('charCount');
    const length = input.value.length;
    charCount.textContent = `${length} / 4000`;
    
    if (length > 3800) {
        charCount.style.color = 'var(--error)';
    } else if (length > 3500) {
        charCount.style.color = 'var(--warning)';
    } else {
        charCount.style.color = 'var(--text-secondary)';
    }
}

// Send suggested prompt
function sendSuggestedPrompt(prompt) {
    const input = document.getElementById('messageInput');
    input.value = prompt;
    input.focus();
    autoResize(input);
    updateCharCount();
    sendMessage();
}

// Clear session
async function clearSession() {
    if (!confirm('Are you sure you want to clear the chat history?')) return;
    
    try {
        const response = await fetch(`/apps/${AGENT_NAME}/users/${SESSION_ID}/sessions/${SESSION_ID}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Clear messages from UI
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.innerHTML = '';
            
            // Reload to get fresh welcome message
            location.reload();
        }
    } catch (error) {
        console.error('Error clearing session:', error);
    }
}

// New chat
function newChat() {
    // Clear session and reload for same agent
    window.location.href = `/chat/${AGENT_NAME}`;
}

// Toggle theme
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
    localStorage.setItem('theme', currentTheme);
}

// Apply theme
function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    const icon = document.querySelector('#themeToggle i');
    icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connectionStatus');
    if (connected) {
        statusBadge.classList.add('connected');
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Connected';
    } else {
        statusBadge.classList.remove('connected');
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
    }
}

// Update agent info
function updateAgentInfo(info) {
    // Update agent details in sidebar if needed
    console.log('Agent info:', info);
    window.AGENT_INFO = info;
}

// Download chat history
function downloadChat() {
    const messages = document.querySelectorAll('.message');
    let chatText = `Chat Export - ${AGENT_NAME} - ${new Date().toLocaleString()}\n\n`;
    
    messages.forEach(msg => {
        const author = msg.querySelector('.message-author').textContent;
        const time = msg.querySelector('.message-time').textContent;
        const body = msg.querySelector('.message-body').textContent;
        
        chatText += `[${time}] ${author}:\n${body}\n\n`;
    });
    
    // Create download
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${AGENT_NAME}-chat-export-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Setup file upload
function setupFileUpload() {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('fileInput');
    
    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragging');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragging');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragging');
        handleFiles(e.dataTransfer.files);
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

// Handle files
function handleFiles(files) {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    
    Array.from(files).forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-item-info">
                <i class="fas fa-file"></i>
                <div>
                    <div class="file-item-name">${file.name}</div>
                    <div class="file-item-size">${formatFileSize(file.size)}</div>
                </div>
            </div>
            <button class="btn-icon" onclick="removeFile(this)">
                <i class="fas fa-times"></i>
            </button>
        `;
        fileList.appendChild(fileItem);
    });
}

// Remove file
function removeFile(button) {
    button.closest('.file-item').remove();
}

// Close file modal
function closeFileModal() {
    document.getElementById('fileModal').style.display = 'none';
    document.getElementById('fileList').innerHTML = '';
    document.getElementById('fileInput').value = '';
}

// Upload files
async function uploadFiles() {
    // Implement file upload logic here
    console.log('Uploading files...');
    closeFileModal();
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Ping to keep connection alive
setInterval(() => {
    if (isConnected && socket) {
        socket.emit('ping');
    }
}, 30000);