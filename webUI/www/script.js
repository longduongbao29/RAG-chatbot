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
const ragStrategySelect = document.getElementById('ragStrategySelect');
const fileUploadBtn = document.querySelector('.chatbar-icon.left');
const fileInput = document.getElementById('fileUploader');
const uploadedFilesList = document.getElementById('uploadedFilesList');
const newChatBtn = document.getElementById('newChatBtn');

// ===============================
// Constants
// ===============================
const API_URL = "https://api.chatbotonline.site/api";
// const API_URL = "http://localhost:1234/api"
const models = {
    groq: [
        { value: "meta-llama/llama-4-scout-17b-16e-instruct", label: "meta-llama/llama-4-scout-17b (Khuyên dùng)" },
        { value: "deepseek-r1-distill-llama-70b", label: "deepseek-r1-distill-llama-70b" },
        { value: "llama-3.3-70b-versatile", label: "llama-3.3-70b-versatile" },
        { value: "llama-3.1-8b-instant", label: "llama-3.1-8b-instant" },
        { value: "llama3-70b-8192", label: "llama3-70b-8192" },
    ],
    openai: [
        { value: "gpt-4.1-nano", label: "gpt-4.1-nano" },
        { value: "gpt-4o-mini", label: "gpt-4o-mini" }
    ]
};

// ===============================
// Initialization
// ===============================
document.addEventListener('DOMContentLoaded', () => {
    restoreTheme();
    restoreSettings();
    restoreChatHistory();
    restoreUploadedFiles()
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
function restoreUploadedFiles() {
    const uploadedFiles = JSON.parse(localStorage.getItem('uploadedFiles')) || [];

    uploadedFiles.forEach(file => {
        const listItem = document.createElement('li');

        const fileIcon = document.createElement('i');
        fileIcon.className = getFileIconClass(file.type); // 👈 icon theo loại file
        fileIcon.style.marginRight = '6px';

        const fileNameSpan = document.createElement('span');
        fileNameSpan.className = 'file-name';
        fileNameSpan.textContent = file.name + ` - ${(file.size / (1024 * 1024)).toFixed(2)} MB`;
        fileNameSpan.prepend(fileIcon); // ⬅️ thêm icon trước tên
        // Xử lý click preview
        fileNameSpan.addEventListener('click', () => {
            if (file.type.startsWith('image/') || file.type === 'application/pdf') {
                window.open(file.url, '_blank');
            }
        });

        listItem.appendChild(fileNameSpan);
        uploadedFilesList.appendChild(listItem);
    });
}

function restoreSettings() {
    if (!localStorage.getItem('session_id')) {
        resetSession()
    }

    const savedProvider = localStorage.getItem('provider') || 'groq';
    providerSelect.value = savedProvider;
    updateModelList(savedProvider);

    const savedTemperature = localStorage.getItem('temperature');
    if (savedTemperature) temperatureInput.value = savedTemperature;

    const savedRAG = localStorage.getItem('rag_strategy') || 'no_rag';
    ragStrategySelect.value = savedRAG;

}

function resetSession() {
    old_session_id = localStorage.getItem('session_id')
    if (old_session_id) {
        try {

            fetch(`${API_URL}/delete_session/${old_session_id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
            })
        } catch (err) {
            console.log(err);
        }
    }
    new_session_id = crypto.randomUUID()
    localStorage.setItem('session_id', new_session_id)
    try {

        fetch(`${API_URL}/create_session/${new_session_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
    } catch (error) {
        console.log(error);

    }

}

function getFileIconClass(fileType) {
    if (fileType.startsWith('image/')) return 'fas fa-file-image';
    if (fileType === 'application/pdf') return 'fas fa-file-pdf';
    if (fileType.startsWith('text/')) return 'fas fa-file-alt';
    return 'fas fa-file'; // Mặc định: biểu tượng file chung
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
    ragStrategySelect.addEventListener('change', () => {
        localStorage.setItem('rag_strategy', ragStrategySelect.value);
    });
    fileUploadBtn.addEventListener('click', () => {
        fileInput.click();
    });
    fileInput.addEventListener('change', async () => {
        const files = Array.from(fileInput.files);
        for (const file of files) {
            const listItem = document.createElement('li');

            const fileIcon = document.createElement('i');
            fileIcon.className = getFileIconClass(file.type); // 👈 icon theo loại file
            fileIcon.style.marginRight = '6px';


            const fileNameSpan = document.createElement('span');
            fileNameSpan.className = 'file-name';
            fileNameSpan.textContent = file.name + `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
            fileNameSpan.prepend(fileIcon); // ⬅️ thêm icon trước tên
            try {
                await uploadfile(file)
                // Cập nhật localStorage
                let uploadedFiles = JSON.parse(localStorage.getItem('uploadedFiles')) || [];
                uploadedFiles.push({
                    name: file.name,
                    type: file.type,
                    size: file.size
                });
                localStorage.setItem('uploadedFiles', JSON.stringify(uploadedFiles));

                // Thêm vào UI
                listItem.appendChild(fileNameSpan);
                uploadedFilesList.appendChild(listItem);
            } catch (error) {
                console.error(error);
                continue;
            }

        }

        fileInput.value = '';
    });
    newChatBtn.addEventListener('click', () => {
        if (confirm("Bạn có chắc muốn bắt đầu cuộc trò chuyện mới?")) {
            chatArea.innerHTML = '';
            uploadedFilesList.innerHTML = ''
            localStorage.removeItem('chatHistory');
            localStorage.removeItem('uploadedFiles')
            resetSession()
        }
    });



}
async function uploadfile(file) {
    // Upload lên server thật
    const formData = new FormData();
    formData.append('session_id', localStorage.getItem("session_id"))
    formData.append('file', file);
    try {
        const res = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        const result = await res.json();
        addMessage('Bot', `Uploaded ${file.name}`);

    } catch (err) {
        console.error("Lỗi upload:", err);
        addMessage('Bot', `Không thể tải lên tệp ${file.name}`);
        throw err;

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
    messageDiv.innerHTML = `
  <div class="message-content with-icon">
    <i class="${sender === 'Bạn' ? 'fas fa-user' : sender === 'Bot' ? 'fas fa-robot' : ''} message-icon-inline"></i>
    <span class="message-text">${text}</span>
  </div>
`;

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
    const session_id = localStorage.getItem("session_id")

    const message = chatInput.value.trim();
    if (!message) return;

    addMessage('Bạn', message);
    chatInput.value = '';

    const loadingMessage = document.createElement('div');
    loadingMessage.classList.add('message', 'bot-message');
    loadingMessage.innerHTML = `<div class="message-content"><i class="fas fa-robot"></i> <span>Đang nhập...</span></div>`;
    chatArea.appendChild(loadingMessage);
    chatArea.scrollTop = chatArea.scrollHeight;
    const requestBody = {
        session_id: session_id,
        rag_strategy: ragStrategySelect.value,      // string
        messages: getChatHistory(),                              // array of { role, message }
        provider: providerSelect.value,                          // "groq" or "openai"
        model_name: modelSelect.value,                           // string
        temperature: parseFloat(temperatureInput.value),         // float
    };
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody),
        });

        chatArea.removeChild(loadingMessage);
        const data = await response.json();
        const parsedAnswer = marked.parse(data.answer || 'Không nhận được phản hồi từ bot.');
        addMessage('Bot', parsedAnswer);
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