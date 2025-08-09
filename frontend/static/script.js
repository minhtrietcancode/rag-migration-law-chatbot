class MigrationChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.themeToggle = document.getElementById('themeToggle');
        
        this.init();
    }

    init() {
        // Initialize theme
        this.initializeTheme();

        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
        });

        // Send message on Enter (Shift+Enter for new line)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Theme toggle click
        this.themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Focus input on load
        this.chatInput.focus();
    }

    initializeTheme() {
        // Check for saved theme preference or default to 'dark'
        const savedTheme = localStorage.getItem('chatbot-theme') || 'dark';
        this.setTheme(savedTheme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('chatbot-theme', theme);
        
        // Add a small animation effect to the toggle button
        this.themeToggle.style.transform = 'scale(0.9)';
        setTimeout(() => {
            this.themeToggle.style.transform = 'scale(1)';
        }, 150);
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Clear input
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';

        // Add user message
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTyping();

        // Disable send button
        this.sendButton.disabled = true;

        try {
            // Send to backend
            const response = await this.callBackend(message);
            
            // Hide typing and show response
            this.hideTyping();
            this.addMessage(response, 'bot');
        } catch (error) {
            this.hideTyping();
            this.addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'bot');
            console.error('Error:', error);
        } finally {
            // Re-enable send button
            this.sendButton.disabled = false;
            this.chatInput.focus();
        }
    }

    async callBackend(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        return data.response;
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        
        // Remove welcome message if it exists
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        // Remove welcome message if it exists
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        this.typingIndicator.style.display = 'block';
        this.chatMessages.appendChild(this.typingIndicator);
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingIndicator.style.display = 'none';
        if (this.typingIndicator.parentNode) {
            this.typingIndicator.parentNode.removeChild(this.typingIndicator);
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    new MigrationChatbot();
});