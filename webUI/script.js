// Lấy các phần tử DOM
const chatArea = document.getElementById('chatArea');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

const modelSelect = document.getElementById('modelSelect');
const temperatureInput = document.getElementById('temperatureInput');
const uploadGroup = document.getElementById('uploadGroup');
const themeToggleBtn = document.getElementById('themeToggleBtn');

const indexNameInput = document.getElementById('indexNameInput'); // Input for index name
const descriptionInput = document.getElementById('descriptionInput');
const fileInput = document.getElementById('fileInput');
const fileNameSpan = document.getElementById('fileName');
const uploadBtn = document.getElementById('uploadBtn');

API_URL = "http://52.194.241.126:8002/api"


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

    // Gửi yêu cầu đến API sau khi người dùng nhập tin nhắn
    fetch(API_URL + "/ask", { // Thay 'https://api.example.com/chat' bằng URL API thực tế của bạn
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: message }) // Gửi câu hỏi (message) dưới dạng JSON
    })
        .then(response => response.json()) // Chuyển phản hồi từ API thành đối tượng JSON
        .then(data => {
            if (data && data.answer) {
                addMessage('Bot', data.answer); // Hiển thị câu trả lời từ API
            } else {
                addMessage('Bot', "Không nhận được phản hồi từ bot.");
            }
        })
        .catch(error => {
            // Xử lý lỗi nếu có
            console.error('Có lỗi xảy ra:', error);
            addMessage('Bot', "Có lỗi xảy ra khi gửi tin nhắn.");
        });
}
// Hiển thị tên file khi người dùng chọn file
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (fileExtension === 'docx' || fileExtension === 'pdf') {
            fileNameSpan.textContent = file.name;
        } else {
            fileInput.value = ""; // Reset file input
            fileNameSpan.textContent = "Vui lòng chọn file .docx hoặc .pdf";
            alert("Chỉ cho phép tải lên file .docx hoặc .pdf");
        }
    } else {
        fileNameSpan.textContent = "Chưa có file nào được chọn";
    }
});

uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    const indexName = indexNameInput.value.trim();
    const description = descriptionInput.value.trim();

    if (!file) {
        addMessage('Hệ thống', "Vui lòng chọn file trước khi upload.");
        return;
    }
    if (!indexName || !description) {
        addMessage('Hệ thống', "Vui lòng nhập tên chỉ mục và mô tả.");
        return;
    }

    // Thêm hiệu ứng loading và vô hiệu hóa nút
    uploadBtn.classList.add('loading');
    uploadBtn.disabled = true;
    addMessage('Hệ thống', `Đang upload file: ${file.name}...`);

    // Prepare query parameters
    const queryParams = new URLSearchParams({
        index_name: indexName,
        description: description
    }).toString();

    // Only include the file in FormData
    const formData = new FormData();
    formData.append('file', file);

    console.log("Query params:", queryParams);
    console.log("FormData contents:");
    for (const [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    try {
        const response = await fetch(`${API_URL}/index?${queryParams}`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            addMessage('Hệ thống', result.message || "Tải tài liệu và lập chỉ mục thành công.");
        } else {
            const errorResult = await response.json();
            console.log("Error response:", JSON.stringify(errorResult, null, 2));
            addMessage('Hệ thống', errorResult.detail || "Có lỗi xảy ra khi tải tài liệu.");
        }

        fileInput.value = "";
        fileNameSpan.textContent = "Chưa có file nào được chọn";
    } catch (error) {
        addMessage('Hệ thống', "Có lỗi xảy ra khi tải tài liệu.");
        console.error("Fetch error:", error);
    } finally {
        // Xóa hiệu ứng loading và kích hoạt lại nút (dù thành công hay lỗi)
        uploadBtn.classList.remove('loading');
        uploadBtn.disabled = false;
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
