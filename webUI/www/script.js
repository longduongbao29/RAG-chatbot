// ===============================
// DOM Element References
// ===============================
const chatArea = document.getElementById('chatArea');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
// const clearChatBtn = document.getElementById('clearChatBtn');
const modelSelect = document.getElementById('modelSelect');
const providerSelect = document.getElementById('providerSelect');
const temperatureInput = document.getElementById('temperatureInput');
const themeToggleBtn = document.getElementById('themeToggleBtn');
const addToolBtn = document.getElementById('addToolBtn');

// ===============================
// Constants
// ===============================
const API_URL = "https://api.chatbotonline.site/api";
const models = {
    groq: [
        { value: "meta-llama/llama-4-scout-17b-16e-instruct", label: "meta-llama/llama-4-scout-17b (Khuyên dùng)" },
        { value: "deepseek-r1-distill-llama-70b", label: "deepseek-r1-distill-llama-70b" },
        { value: "llama-3.3-70b-versatile", label: "llama-3.3-70b-versatile" },
        { value: "llama-3.1-8b-instant", label: "llama-3.1-8b-instant" },
        { value: "llama3-70b-8192", label: "llama3-70b-8192" },
    ],
    openai: [
        { value: "gpt-4o-mini", label: "gpt-4o-mini" }
    ]
};

// ===============================
// Initialization
// ===============================
document.addEventListener('DOMContentLoaded', () => {
    restoreTheme();
    restoreSettings();
    // restoreChatHistory();
    bindEvents();
});

function restoreTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.add(`theme-${savedTheme}`);
    themeToggleBtn.checked = savedTheme === 'dark';
}

function restoreChatHistory() {
    const savedChat = localStorage.getItem('chatHistory');
    if (savedChat) {
        chatArea.innerHTML = savedChat;
        chatArea.scrollTop = chatArea.scrollHeight;
    }
}

function restoreSettings() {
    const savedProvider = localStorage.getItem('provider') || 'groq';
    providerSelect.value = savedProvider;
    updateModelList(savedProvider);

    const savedTemperature = localStorage.getItem('temperature');
    if (savedTemperature) temperatureInput.value = savedTemperature;
}

function bindEvents() {
    themeToggleBtn.addEventListener('change', toggleTheme);
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // clearChatBtn.addEventListener('click', clearChat);
    providerSelect.addEventListener('change', e => updateModelList(e.target.value));
    modelSelect.addEventListener('change', () => localStorage.setItem('model_name', modelSelect.value));
    temperatureInput.addEventListener('input', () => localStorage.setItem('temperature', temperatureInput.value));

    if (addToolBtn) {
        addToolBtn.addEventListener('click', () => {
            alert("Chức năng thêm tài liệu sẽ sớm khả dụng!");
        });
    }
}

// ===============================
// Theme Handling
// ===============================
function toggleTheme() {
    const newTheme = themeToggleBtn.checked ? 'dark' : 'light';
    document.body.classList.remove('theme-light', 'theme-dark');
    document.body.classList.add(`theme-${newTheme}`);
    localStorage.setItem('theme', newTheme);
}

// ===============================
// Chat Functions
// ===============================
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender === 'Bạn' ? 'user' : sender === 'Bot' ? 'bot' : 'system'}-message`);
    const icon = sender === 'Bạn' ? '<i class="fas fa-user"></i>' : sender === 'Bot' ? '<i class="fas fa-robot"></i>' : '';
    messageDiv.innerHTML = `<div class="message-content">${icon} <span>${text}</span></div>`;
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
    localStorage.setItem('chatHistory', chatArea.innerHTML);
}

function getChatHistory() {
    const messages = [];
    chatArea.querySelectorAll('.message').forEach(el => {
        const content = el.querySelector('.message-content span').textContent;
        const role = el.classList.contains('user-message') ? 'user' : 'assistant';
        messages.push({ role, message: content });
    });
    if (messages.length > 0) messages.pop(); // Remove loading message
    return messages;
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    const model_name = modelSelect.value;
    const temperature = parseFloat(temperatureInput.value);

    addMessage('Bạn', message);
    chatInput.value = '';

    const loadingMessage = document.createElement('div');
    loadingMessage.classList.add('message', 'bot-message');
    loadingMessage.innerHTML = `<div class="message-content"><i class="fas fa-robot"></i> <span>Đang nhập...</span></div>`;
    chatArea.appendChild(loadingMessage);
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: getChatHistory(),
                model_name,
                temperature,
                tools: ["milvus_search", "duckduckgo_search", "datetime_tool"]
            })
        });

        chatArea.removeChild(loadingMessage);
        const data = await response.json();
        addMessage('Bot', data.answer || 'Không nhận được phản hồi từ bot.');
    } catch (err) {
        chatArea.removeChild(loadingMessage);
        addMessage('Bot', `Có lỗi xảy ra khi gửi tin nhắn: ${err.message}`);
    }
}


// ===============================
// Model / Provider Functions
// ===============================
function updateModelList(provider) {
    const savedModel = localStorage.getItem('model_name');
    modelSelect.innerHTML = '';
    models[provider].forEach(model => {
        const opt = document.createElement('option');
        opt.value = model.value;
        opt.textContent = model.label;
        modelSelect.appendChild(opt);
    });

    const validModels = models[provider].map(m => m.value);
    if (savedModel && validModels.includes(savedModel)) {
        modelSelect.value = savedModel;
    } else {
        modelSelect.value = models[provider][0].value;
    }

    localStorage.setItem('provider', provider);
    localStorage.setItem('model_name', modelSelect.value);
}