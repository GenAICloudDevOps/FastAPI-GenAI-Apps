// Auto-scroll to bottom when new messages are added
function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Clear input after form submission
document.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.xhr.status === 200) {
        // Clear the input field
        const input = document.querySelector('.chat-input');
        if (input) {
            input.value = '';
        }
        
        // Scroll to bottom
        setTimeout(scrollToBottom, 100);
    }
});

// Handle Enter key submission
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.querySelector('.chat-input');
    
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = this.closest('form');
                if (form && this.value.trim()) {
                    // Trigger HTMX form submission
                    htmx.trigger(form, 'submit');
                }
            }
        });
    }
    
    // Set status to connected on page load
    const statusIndicator = document.getElementById('status');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('span');
    
    statusDot.style.background = '#4ade80';
    statusText.textContent = 'Connected';
});

// Add visual feedback for form submission
document.addEventListener('htmx:beforeRequest', function(event) {
    const sendButton = document.querySelector('.send-button');
    if (sendButton) {
        sendButton.style.opacity = '0.7';
        sendButton.style.transform = 'scale(0.95)';
    }
});

document.addEventListener('htmx:afterRequest', function(event) {
    const sendButton = document.querySelector('.send-button');
    if (sendButton) {
        sendButton.style.opacity = '1';
        sendButton.style.transform = 'scale(1)';
    }
});

// Add animation classes to new messages
document.addEventListener('htmx:afterSwap', function(event) {
    const newMessages = event.target.querySelectorAll('.message');
    newMessages.forEach((message, index) => {
        setTimeout(() => {
            message.style.animationDelay = `${index * 0.1}s`;
        }, 50);
    });
});

// Prevent form submission with empty messages
document.addEventListener('htmx:configRequest', function(event) {
    const formData = new FormData(event.detail.elt);
    const message = formData.get('message');
    
    if (!message || !message.trim()) {
        event.preventDefault();
        return false;
    }
});
