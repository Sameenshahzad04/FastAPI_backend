let ws = null;
let token = null;
let currentUser = null;



document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail);
        }
        
        const data = await response.json();
        
        // Save token and user info to localStorage
        localStorage.setItem('chat_token', data.access_token);
        localStorage.setItem('chat_username', data.username);
        localStorage.setItem('chat_user_id', data.user_id);
        
        // Redirect to chat page
        window.location.href = '/chat.html';
        
    } catch (error) {
        document.getElementById('login-error').textContent = error.message;
    }
});
// document.getElementById('login-form').addEventListener('submit', async (e) => {
//     e.preventDefault();
    
//     const username = document.getElementById('username').value;
//     const password = document.getElementById('password').value;
    
//     try {
//         const response = await fetch('/auth/login', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ username, password })
//         });
        
//         if (!response.ok) {
//             const data = await response.json();
//             throw new Error(data.detail);
//         }
        
//         const data = await response.json();
//         token = data.access_token;
//         currentUser = data.username;
        
//         document.getElementById('login-screen').classList.add('hidden');
//         document.getElementById('chat-screen').classList.remove('hidden');
        
//         connectWebSocket(token);
        
//     } catch (error) {
//         document.getElementById('login-error').textContent = error.message;
//     }
// });

function connectWebSocket(token) {
    ws = new WebSocket(`ws://localhost:8000/chat/ws?token=${token}`);
    
    ws.onopen = () => {
        addMessage('system', ' Connected to chat!');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'user_joined') {
            addMessage('system', ` ${data.username} joined`);
        } else if (data.type === 'user_left') {
            addMessage('system', ` ${data.username} left`);
        } else if (data.type === 'message') {
            addMessage('received', `${data.from_username}: ${data.content}`);
        }
    };
    
    ws.onclose = () => {
        document.getElementById('connection-status').textContent = '🔴 Disconnected';
        addMessage('system', ' Disconnected');
    };
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content || !ws) return;
    
    ws.send(content);
    addMessage('sent', `You: ${content}`);
    input.value = '';
}

function addMessage(type, text) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showRegister() {
    alert('Register endpoint: POST /auth/register');
}