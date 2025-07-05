// DieAI Chat Interface JavaScript

class DieAIChat {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.searchToggle = document.getElementById('search-toggle');
        this.clearButton = document.getElementById('clear-chat');
        this.loadingSpinner = document.getElementById('loading-spinner');

        this.isLoading = false;
        this.conversationHistory = [];

        this.initializeEventListeners();
        this.addWelcomeMessage();
    }

    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Enter key press
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Clear chat button
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => this.clearChat());
        }

        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => this.autoResizeTextarea());
    }

    addWelcomeMessage() {
        const welcomeMessage = {
            role: 'assistant',
            content: 'Hello! I\'m DieAI, your custom transformer-based AI assistant. How can I help you today?'
        };

        this.addMessage(welcomeMessage);
    }

    async sendMessage() {
        if (this.isLoading) return;

        const message = this.chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        const userMessage = {
            role: 'user',
            content: message
        };

        this.addMessage(userMessage);
        this.conversationHistory.push(userMessage);

        // Clear input
        this.chatInput.value = '';
        this.autoResizeTextarea();

        // Show loading
        this.setLoading(true);

        try {
            // Get response from API
            const response = await this.getAIResponse(message);

            // Add assistant response
            const assistantMessage = {
                role: 'assistant',
                content: response.response || 'I apologize, but I encountered an error processing your request.'
            };

            this.addMessage(assistantMessage);
            this.conversationHistory.push(assistantMessage);

        } catch (error) {
            console.error('Error sending message:', error);

            const errorMessage = {
                role: 'assistant',
                content: 'I apologize, but I encountered an error processing your request. Please try again.'
            };

            this.addMessage(errorMessage);

        } finally {
            this.setLoading(false);
        }
    }

    async getAIResponse(message) {
        const useSearch = this.searchToggle ? this.searchToggle.checked : false;

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                use_search: useSearch,
                context: this.getRecentContext()
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    getRecentContext() {
        // Get last 5 messages for context
        const recentMessages = this.conversationHistory.slice(-5);
        return recentMessages.map(msg => `${msg.role}: ${msg.content}`).join('\n');
    }

    addMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.role}`;

        // Create avatar
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = message.role === 'user' ? 'U' : 'AI';

        // Create content
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = this.formatMessageContent(message.content);

        // Append elements based on role
        if (message.role === 'user') {
            messageElement.appendChild(content);
            messageElement.appendChild(avatar);
        } else {
            messageElement.appendChild(avatar);
            messageElement.appendChild(content);
        }

        // Add animation class
        messageElement.classList.add('animate-fade-in-up');

        // Append to chat
        this.chatMessages.appendChild(messageElement);

        // Scroll to bottom
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // Basic formatting for better readability
        content = content.replace(/\n/g, '<br>');

        // Make URLs clickable
        content = content.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // Format code blocks
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');

        return content;
    }

    setLoading(loading) {
        this.isLoading = loading;

        if (loading) {
            this.sendButton.disabled = true;
            this.chatInput.disabled = true;
            this.loadingSpinner.style.display = 'block';

            // Add typing indicator
            this.addTypingIndicator();
        } else {
            this.sendButton.disabled = false;
            this.chatInput.disabled = false;
            this.loadingSpinner.style.display = 'none';

            // Remove typing indicator
            this.removeTypingIndicator();
        }
    }

    addTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'message assistant typing-indicator';
        typingElement.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="typing-animation">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        this.chatMessages.appendChild(typingElement);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = this.chatMessages.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    clearChat() {
        this.chatMessages.innerHTML = '';
        this.conversationHistory = [];
        this.addWelcomeMessage();
    }

    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    exportChat() {
        const chatData = {
            timestamp: new Date().toISOString(),
            messages: this.conversationHistory
        };

        const blob = new Blob([JSON.stringify(chatData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dieai-chat-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// API Chat Interface for external use
class DieAIAPIChat {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = '/api';
    }

    async sendMessage(message, options = {}) {
        const {
            useSearch = false,
            maxLength = 512,
            temperature = 0.8,
            context = null
        } = options;

        const response = await fetch(`${this.baseURL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            body: JSON.stringify({
                message,
                use_search: useSearch,
                max_length: maxLength,
                temperature,
                context
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return await response.json();
    }

    async batchSendMessages(messages, options = {}) {
        const response = await fetch(`${this.baseURL}/batch_chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            body: JSON.stringify({
                messages,
                ...options
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return await response.json();
    }

    async search(query, maxResults = 10) {
        const response = await fetch(`${this.baseURL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            body: JSON.stringify({
                query,
                max_results: maxResults
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return await response.json();
    }

    async getModels() {
        const response = await fetch(`${this.baseURL}/models`, {
            headers: {
                'X-API-Key': this.apiKey
            }
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return await response.json();
    }

    async getUsage() {
        const response = await fetch(`${this.baseURL}/usage`, {
            headers: {
                'X-API-Key': this.apiKey
            }
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return await response.json();
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertElement, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.remove();
        }
    }, 5000);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(() => {
        showAlert('Failed to copy to clipboard', 'error');
    });
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('chat-messages')) {
        window.dieaiChat = new DieAIChat();
    }
});

// Add CSS for typing animation
const style = document.createElement('style');
style.textContent = `
    .typing-animation {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 8px 0;
    }

    .typing-animation span {
        height: 8px;
        width: 8px;
        background: #007bff;
        border-radius: 50%;
        display: inline-block;
        animation: typing 1.4s infinite ease-in-out;
    }

    .typing-animation span:nth-child(1) {
        animation-delay: -0.32s;
    }

    .typing-animation span:nth-child(2) {
        animation-delay: -0.16s;
    }

    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

function submitFeedback(feedbackType, messageId, userMessage, aiResponse) {
    fetch('/api/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('api_key')}`
        },
        body: JSON.stringify({
            conversation_id: messageId,
            user_message: userMessage,
            ai_response: aiResponse,
            feedback_type: feedbackType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showToast('Thank you for your feedback! This helps me learn.', 'success');
        }
    })
    .catch(error => {
        console.error('Feedback error:', error);
    });
}

function showCorrectionModal(messageId, userMessage, aiResponse) {
    const correctionText = prompt('How should I have responded instead?');
    if (correctionText && correctionText.trim()) {
        submitFeedback('correction', messageId, userMessage, aiResponse, correctionText);
    }
}

function submitFeedback(feedbackType, messageId, userMessage, aiResponse, correctionText = null) {
    const payload = {
        conversation_id: messageId,
        user_message: userMessage,
        ai_response: aiResponse,
        feedback_type: feedbackType
    };

    if (correctionText) {
        payload.correction_text = correctionText;
    }

    fetch('/api/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('api_key')}`
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            const message = correctionText ? 
                'Thank you for the correction! I\'ll learn from this.' : 
                'Thank you for your feedback! This helps me learn.';
            showToast(message, 'success');
        }
    })
    .catch(error => {
        console.error('Feedback error:', error);
        showToast('Error submitting feedback', 'error');
    });
}

function showToast(message, type) {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}