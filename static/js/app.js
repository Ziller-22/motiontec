// ZENO Personal AI Assistant - JavaScript Functions

class ZenoApp {
    constructor() {
        this.isListening = false;
        this.currentMode = 'conversation';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSystemStatus();
    }

    setupEventListeners() {
        // Chat form submission
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => this.handleChatSubmit(e));
        }

        // Voice button
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoiceRecording());
        }

        // Mode selection
        document.querySelectorAll('.mode-option').forEach(option => {
            option.addEventListener('click', (e) => this.changeMode(e));
        });

        // Quick commands
        document.querySelectorAll('.quick-command').forEach(btn => {
            btn.addEventListener('click', (e) => this.executeQuickCommand(e));
        });

        // Enter key in message input
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    chatForm.dispatchEvent(new Event('submit'));
                }
            });
        }
    }

    async handleChatSubmit(e) {
        e.preventDefault();
        
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        // Clear input and disable send button
        messageInput.value = '';
        this.toggleSendButton(false);
        
        // Add user message to chat
        this.addMessageToChat('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            if (response.ok) {
                // Add assistant response
                this.addMessageToChat('assistant', data.content, data.type);
                
                // Speak response if TTS is available
                if (data.content && data.type !== 'error') {
                    this.speakText(data.content);
                }
                
                // Update mode if changed
                if (data.mode !== this.currentMode) {
                    this.updateCurrentMode(data.mode);
                }
            } else {
                this.addMessageToChat('error', data.error || 'An error occurred');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessageToChat('error', 'Network error. Please try again.');
            console.error('Chat error:', error);
        } finally {
            this.toggleSendButton(true);
            messageInput.focus();
        }
    }

    addMessageToChat(sender, content, type = null) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'p-3';
        
        const timestamp = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        let avatarIcon = 'bi-person';
        let messageClass = 'user-message';
        
        if (sender === 'assistant') {
            avatarIcon = 'bi-robot';
            messageClass = 'assistant-message';
        } else if (sender === 'system') {
            avatarIcon = 'bi-gear';
            messageClass = 'system-message';
        } else if (sender === 'error') {
            avatarIcon = 'bi-exclamation-triangle';
            messageClass = 'error-message';
        }
        
        messageDiv.innerHTML = `
            <div class="message-bubble ${messageClass}">
                <div class="d-flex align-items-start ${sender === 'user' ? 'flex-row-reverse' : ''}">
                    <div class="avatar bg-primary rounded-circle d-flex align-items-center justify-content-center ${sender === 'user' ? 'ms-2' : 'me-2'}" style="width: 32px; height: 32px;">
                        <i class="${avatarIcon} text-white small"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="message-content text-white rounded p-2">
                            ${this.formatMessageContent(content)}
                        </div>
                        <small class="text-muted">${timestamp}</small>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // Basic formatting for message content
        return content
            .replace(/\n/g, '<br>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'p-3';
        typingDiv.innerHTML = `
            <div class="message-bubble assistant-message">
                <div class="d-flex align-items-start">
                    <div class="avatar bg-primary rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px;">
                        <i class="bi bi-robot text-white small"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="message-content bg-primary text-white rounded p-2">
                            <div class="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    toggleSendButton(enabled) {
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            sendBtn.disabled = !enabled;
        }
    }

    async toggleVoiceRecording() {
        const voiceBtn = document.getElementById('voice-btn');
        const voiceRecording = document.getElementById('voice-recording');
        
        if (!this.isListening) {
            // Start recording
            try {
                const response = await fetch('/api/speech/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.isListening = true;
                    voiceBtn.classList.add('recording');
                    voiceBtn.innerHTML = '<i class="bi bi-stop-fill"></i>';
                    voiceRecording.classList.remove('d-none');
                } else {
                    this.showToast('Speech recognition not available', 'warning');
                }
            } catch (error) {
                this.showToast('Error starting speech recognition', 'error');
                console.error('Speech start error:', error);
            }
        } else {
            // Stop recording
            try {
                const response = await fetch('/api/speech/stop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                this.isListening = false;
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
                voiceRecording.classList.add('d-none');
                
                if (data.text && data.text.trim()) {
                    // Put recognized text in input field
                    const messageInput = document.getElementById('message-input');
                    messageInput.value = data.text;
                    messageInput.focus();
                    
                    // Auto-submit if it looks like a command
                    if (data.text.toLowerCase().includes('zeno')) {
                        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
                    }
                }
            } catch (error) {
                this.isListening = false;
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
                voiceRecording.classList.add('d-none');
                this.showToast('Error stopping speech recognition', 'error');
                console.error('Speech stop error:', error);
            }
        }
    }

    async speakText(text) {
        try {
            await fetch('/api/speech/speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
        } catch (error) {
            console.error('TTS error:', error);
        }
    }

    async changeMode(e) {
        e.preventDefault();
        const mode = e.target.dataset.mode;
        
        try {
            const response = await fetch('/api/mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: mode })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateCurrentMode(mode);
                this.showToast(`Switched to ${mode} mode`, 'success');
                this.addMessageToChat('system', `Mode changed to ${mode}`);
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast('Error changing mode', 'error');
            console.error('Mode change error:', error);
        }
    }

    updateCurrentMode(mode) {
        this.currentMode = mode;
        const currentModeElement = document.getElementById('current-mode');
        if (currentModeElement) {
            currentModeElement.textContent = mode.charAt(0).toUpperCase() + mode.slice(1);
        }
    }

    executeQuickCommand(e) {
        const command = e.target.dataset.command || e.target.closest('.quick-command').dataset.command;
        const messageInput = document.getElementById('message-input');
        
        messageInput.value = command;
        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            // Update status indicators
            this.updateStatusIndicators(status);
            
        } catch (error) {
            console.error('Status load error:', error);
        }
    }

    updateStatusIndicators(status) {
        // Update Ollama status
        const ollamaStatus = document.getElementById('ollama-status');
        if (ollamaStatus) {
            const isAvailable = status.model_status?.ollama_available;
            ollamaStatus.innerHTML = `
                <i class="bi bi-${isAvailable ? 'check-circle text-success' : 'x-circle text-danger'} fs-4"></i>
                <div class="small">Ollama</div>
            `;
        }
        
        // Update overall status indicator
        const statusIndicator = document.getElementById('status-indicator');
        if (statusIndicator) {
            const isOnline = status.active;
            statusIndicator.className = `badge bg-${isOnline ? 'success' : 'danger'}`;
            statusIndicator.innerHTML = `<i class="bi bi-circle-fill"></i> ${isOnline ? 'Online' : 'Offline'}`;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastBody = toast.querySelector('.toast-body');
        
        // Set message and style
        toastBody.textContent = message;
        toast.className = `toast bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} text-white`;
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    clearChat() {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="p-3">
                <div class="message-bubble assistant-message">
                    <div class="d-flex align-items-start">
                        <div class="avatar bg-primary rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px;">
                            <i class="bi bi-robot text-white small"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="message-content bg-primary text-white rounded p-2">
                                <p class="mb-0">Chat cleared. How can I help you?</p>
                            </div>
                            <small class="text-muted">Just now</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// Global functions for template usage
function clearChat() {
    app.clearChat();
}

function refreshModels() {
    fetch('/api/models/refresh', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            app.showToast('Models refreshed', 'success');
            app.loadSystemStatus();
        })
        .catch(error => {
            app.showToast('Error refreshing models', 'error');
            console.error('Model refresh error:', error);
        });
}

function loadSystemStatus() {
    app.loadSystemStatus();
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new ZenoApp();
});