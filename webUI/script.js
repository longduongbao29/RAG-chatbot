// Lấy các phần tử DOM
const chatArea = document.getElementById('chatArea');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

const chatModeSelect = document.getElementById('chatModeSelect');
const modelSelect = document.getElementById('modelSelect');
const temperatureInput = document.getElementById('temperatureInput');
const fileInput = document.getElementById('fileInput');
const uploadGroup = document.getElementById('uploadGroup');
const fileNameSpan = document.getElementById('fileName');
const uploadBtn = document.getElementById('uploadBtn');
const themeToggleBtn = document.getElementById('themeToggleBtn');

let currentMode = chatModeSelect.value;

// Hiển thị hoặc ẩn phần upload file dựa trên chế độ chat
chatModeSelect.addEventListener('change', () => {
    currentMode = chatModeSelect.value;
    uploadGroup.style.display = (currentMode === 'document') ? 'flex' : 'none';
    chatArea.innerHTML = ''; // Xoá nội dung chat khi chuyển đổi chế độ
});

// Hàm thêm tin nhắn vào khung chat
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    let icon = '';
    if (sender === "Bạn") {
        messageDiv.classList.add("message", "user-message");
        icon = `<i class="fas fa-user"></i>`;
    } else if (sender === "Bot") {
        messageDiv.classList.add("message", "bot-message");
        icon = `<i class="fas fa-robot"></i>`;
    } else {
        messageDiv.classList.add("message", "system-message");
    }
    messageDiv.innerHTML = `<div class="message-content">${icon} <span>${text}</span></div>`;
    chatArea.appendChild(messageDiv);
    // Tự động cuộn xuống cuối
    chatArea.scrollTop = chatArea.scrollHeight;
}


// Xử lý gửi tin nhắn khi click vào nút hoặc nhấn Enter
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const message = chatInput.value.trim();
    if (message === '') return;
    addMessage('Bạn', message);
    chatInput.value = '';

    // Giả lập phản hồi của Bot sau 500ms
    setTimeout(() => {
        let response;
        if (currentMode === 'normal') {
            response = "Phản hồi cho chế độ Chat Thông Thường.";
        } else if (currentMode === 'document') {
            response = "Phản hồi cho chế độ Chat với Tài liệu.";
        }
        addMessage('Bot', response);
    }, 500);
}

// Hiển thị tên file khi người dùng chọn file
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        fileNameSpan.textContent = file.name;
    } else {
        fileNameSpan.textContent = "Chưa có file nào được chọn";
    }
});

// Xử lý sự kiện upload file
uploadBtn.addEventListener('click', () => {
    const file = fileInput.files[0];
    if (file) {
        addMessage('Hệ thống', `Đã upload file: ${file.name}`);
        // Sau khi xử lý upload, reset file input
        fileInput.value = "";
        fileNameSpan.textContent = "Chưa có file nào được chọn";
    } else {
        addMessage('Hệ thống', "Vui lòng chọn file trước khi upload.");
    }
});

// Xử lý chuyển theme khi bấm nút
themeToggleBtn.addEventListener('click', () => {
    if (document.body.classList.contains("theme-light")) {
        document.body.classList.remove("theme-light");
        document.body.classList.add("theme-dark");
        themeToggleBtn.textContent = "☀️"; // Icon chuyển về light
    } else {
        document.body.classList.remove("theme-dark");
        document.body.classList.add("theme-light");
        themeToggleBtn.textContent = "🌙"; // Icon chuyển về dark
    }
});

const clearChatBtn = document.getElementById('clearChatBtn');

clearChatBtn.addEventListener('click', () => {
    chatArea.innerHTML = '';

    const messageDiv = document.createElement('div');
    messageDiv.classList.add("message", "system-message");
    messageDiv.innerHTML = `<div class="message-content"><span>Đã xoá toàn bộ nội dung chat.</span></div>`;
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;

    // Tự động ẩn sau 2 giây
    setTimeout(() => {
        chatArea.removeChild(messageDiv);
    }, 2000);
});
