const chatWindow = document.getElementById('chatWindow');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const imageBtn = document.getElementById('imageBtn');
const voiceBtn = document.getElementById('voiceBtn');
const imageInput = document.getElementById('imageInput');
const voiceInput = document.getElementById('voiceInput');

const API_URL = 'http://localhost:8000/api/message';

// Add message to chat
function addMessage(sender, content, type = 'text') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (type === 'text') {
        contentDiv.textContent = content;
    } else if (type === 'image') {
        const img = document.createElement('img');
        img.className = 'message-image';
        img.src = content;
        contentDiv.appendChild(img);
    } else if (type === 'voice') {
        const fileTag = document.createElement('div');
        fileTag.className = 'message-file';
        fileTag.textContent = `Voice: ${content}`;
        contentDiv.appendChild(fileTag);
    }

    bubble.appendChild(contentDiv);
    messageDiv.appendChild(bubble);
    chatWindow.appendChild(messageDiv);

    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Send message to backend
async function sendToBackend(payload) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Backend request failed');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
        return { response: 'Error: Could not reach backend server.' };
    }
}

// Handle text message
async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage('user', message, 'text');
    messageInput.value = '';

    sendBtn.disabled = true;

    const payload = {
        message: message,
        sender_phone: '+1234567890',  // Demo phone number
        case_id: null
    };

    const response = await sendToBackend(payload);
    addMessage('assistant', response.response || 'No response from server', 'text');

    sendBtn.disabled = false;
}

// Handle image upload
async function handleImageUpload(file) {
    // Show image preview in chat
    const reader = new FileReader();
    reader.onload = function (e) {
        addMessage('user', e.target.result, 'image');
    };
    reader.readAsDataURL(file);

    // Send to backend using FormData
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('sender_phone', '+1234567890'); // Demo phone number
        // formData.append('case_id', null); // Optional: add case_id if continuing conversation

        const response = await fetch('http://localhost:8000/api/upload', {
            method: 'POST',
            body: formData
            // Don't set Content-Type header - browser will set it with boundary
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Upload failed:', errorText);
            addMessage('assistant', 'Error: Could not process image.', 'text');
            return;
        }

        const data = await response.json();
        addMessage('assistant', data.response || 'Image processed successfully', 'text');
    } catch (error) {
        console.error('Upload error:', error);
        addMessage('assistant', 'Error: Could not reach backend server.', 'text');
    }
}

// Handle voice upload
async function handleVoiceUpload(file) {
    addMessage('user', file.name, 'voice');

    const payload = {
        sender: 'user',
        message_type: 'voice',
        content: file.name
    };

    const response = await sendToBackend(payload);
    addMessage('assistant', response.response || 'Voice file received', 'text');
}

// Event listeners
sendBtn.addEventListener('click', handleSendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});

imageBtn.addEventListener('click', () => {
    imageInput.click();
});

voiceBtn.addEventListener('click', () => {
    voiceInput.click();
});

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleImageUpload(file);
    }
    imageInput.value = '';
});

voiceInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleVoiceUpload(file);
    }
    voiceInput.value = '';
});