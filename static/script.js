// Generate a simple session ID or retrieve from localStorage
let sessionId = localStorage.getItem('arun_session_id');
if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('arun_session_id', sessionId);
}

const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

// Auto-resize textarea
chatInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight < 150 ? this.scrollHeight : 150) + 'px';
});

// Handle enter key to send
chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function startNewChat() {
    sessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('arun_session_id', sessionId);
    chatHistory.innerHTML = `
        <div class="message ai-message">
            <div class="message-content">
                Hey! I'm Arun's AI. I know exactly what he's working on, his skills, and his goals. Let's start a fresh chat. How can I help you today?
            </div>
        </div>
    `;
}

function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (role === 'ai') {
        contentDiv.innerHTML = marked.parse(content);
    } else {
        contentDiv.textContent = content; // pure text for user
    }
    
    msgDiv.appendChild(contentDiv);
    chatHistory.appendChild(msgDiv);
    scrollToBottom();
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator message';
    typingDiv.id = 'typing';
    typingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatHistory.appendChild(typingDiv);
    scrollToBottom();
}

function removeTyping() {
    const typing = document.getElementById('typing');
    if (typing) typing.remove();
}

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Reset input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Append user message
    appendMessage('user', text);
    showTyping();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                session_id: sessionId
            })
        });

        const data = await response.json();
        removeTyping();
        
        if (response.ok) {
            appendMessage('ai', data.response);
        } else {
            appendMessage('ai', "I had a tiny glitch connecting to my server. Could you repeat that?");
        }

    } catch (err) {
        removeTyping();
        appendMessage('ai', "My API seems unreachable right now. Please check if the backend is running.");
        console.error("Chat Error:", err);
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}
