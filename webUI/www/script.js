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

const selectedModel = modelSelect.value;
const temperature = temperatureInput.value;

// API_URL = "http://localhost:8000/api"
API_URL = process.env.BACKEND_URL || "http://localhost:8000/api";

document.addEventListener('DOMContentLoaded', () => {
    const savedChat = localStorage.getItem('chatHistory');
    if (savedChat) {
        chatArea.innerHTML = savedChat;
        chatArea.scrollTop = chatArea.scrollHeight;
    }
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
    chatArea.scrollTop = chatArea.scrollHeight;

    // Lưu lịch sử chat vào localStorage
    localStorage.setItem('chatHistory', chatArea.innerHTML);
}

// Xử lý gửi tin nhắn khi click vào nút hoặc nhấn Enter
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
function getChatHistory() {
    const messages = [];
    const messageElements = chatArea.querySelectorAll('.message');
    messageElements.forEach((element) => {
        const content = element.querySelector('.message-content span').textContent;
        const isUser = element.classList.contains('user-message');
        messages.push({
            role: isUser ? 'user' : 'assistant',
            message: content,
        });
    });
    if (messages.length > 0) {
        messages.pop();
    }
    return messages;
}
async function sendMessage() {
    const message = chatInput.value.trim();
    const model_name = modelSelect.value;
    const temperature = temperatureInput.value;
    const use_rag = document.getElementById('ragToggle').checked;
    if (message === '') return;
    addMessage('Bạn', message);
    chatInput.value = '';

    // Thêm tin nhắn "Đang nhập..." với hiệu ứng tạm thời
    const loadingMessage = document.createElement('div');
    loadingMessage.classList.add("message", "bot-message");
    loadingMessage.innerHTML = `<div class="message-content"><i class="fas fa-robot"></i> <span>Đang nhập...</span></div>`;
    chatArea.appendChild(loadingMessage);
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
        const history = getChatHistory();

        const response = await fetch(API_URL + "/chat", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: history,
                model_name: model_name,
                temperature: parseFloat(temperature),
                tools : ["milvus_search", "duckduckgo_search", "datetime_tool"],
                use_retrieve: use_rag
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        chatArea.removeChild(loadingMessage); // Xóa tin nhắn "Đang nhập..."
        if (data && data.answer) {
            addMessage('Bot', data.answer);
        } else {
            addMessage('Bot', "Không nhận được phản hồi từ bot.");
        }
    } catch (error) {
        chatArea.removeChild(loadingMessage);
        addMessage('Bot', "Có lỗi xảy ra khi gửi tin nhắn: " + error.message);
    }

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

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang upload...';

    if (!file || !indexName || !description) {
        addMessage('Hệ thống', "Vui lòng điền đầy đủ thông tin và chọn file.");
        return;
    }

    uploadBtn.disabled = true;
    addMessage('Hệ thống', `Đang upload file: ${file.name}...`);

    // Thêm thanh tiến trình
    const progressBar = document.createElement('div');
    progressBar.classList.add('progress-bar');
    const progressFill = document.createElement('div');
    progressFill.classList.add('progress-bar-fill');
    progressBar.appendChild(progressFill);
    uploadGroup.appendChild(progressBar);

    const formData = new FormData();
    formData.append('file', file);
    const queryParams = new URLSearchParams({
        index_name: indexName,
        description: description
    }).toString();

    try {
        const response = await fetch(`${API_URL}/index?${queryParams}`, {
            method: 'POST',
            body: formData
        });

        // Giả lập tiến trình (thay bằng logic thực tế nếu API hỗ trợ)
        let progress = 0;
        const interval = setInterval(() => {
            progress += 20;
            progressFill.style.width = `${progress}%`;
            if (progress >= 100) clearInterval(interval);
        }, 500);

        if (response.ok) {
            const result = await response.json();
            addMessage('Hệ thống', result.message || "Tải tài liệu và lập chỉ mục thành công.");
        } else {
            const errorResult = await response.json();
            addMessage('Hệ thống', errorResult.detail || "Có lỗi xảy ra khi tải tài liệu.");
        }
    } catch (error) {
        addMessage('Hệ thống', "Có lỗi xảy ra: " + error.message);
    } finally {
        uploadBtn.disabled = false;
        setTimeout(() => uploadGroup.removeChild(progressBar), 2000); // Xóa thanh tiến trình sau 2 giây
        fileInput.value = "";
        fileNameSpan.textContent = "Chưa có file nào được chọn";
        uploadBtn.innerHTML = '<i class="fas fa-cloud-upload-alt"></i> Upload';
    }
});


const clearChatBtn = document.getElementById('clearChatBtn');

clearChatBtn.addEventListener('click', () => {
    chatArea.innerHTML = '';
    localStorage.removeItem('chatHistory'); // Xóa lịch sử trong localStorage

    const messageDiv = document.createElement('div');
    messageDiv.classList.add("message", "system-message");
    messageDiv.innerHTML = `<div class="message-content"><span>Đã xoá toàn bộ nội dung chat.</span></div>`;
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;

    setTimeout(() => {
        chatArea.removeChild(messageDiv);
    }, 2000);
});



document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('theme-dark');
        themeToggleBtn.checked = true; // Đặt checkbox thành "bật"
    } else {
        document.body.classList.add('theme-light');
        themeToggleBtn.checked = false; // Đặt checkbox thành "tắt"
    }
});

// Xử lý khi người dùng bật/tắt công tắc
themeToggleBtn.addEventListener('change', () => {
    if (themeToggleBtn.checked) {
        document.body.classList.remove('theme-light');
        document.body.classList.add('theme-dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.classList.remove('theme-dark');
        document.body.classList.add('theme-light');
        localStorage.setItem('theme', 'light');
    }
});



modelSelect.addEventListener('change', () => {
    localStorage.setItem('model_name', selectedModel); // Lưu vào localStorage
    localStorage.setItem('temperature', temperature); // Lưu vào localStorage
});


temperatureInput.addEventListener('input', () => {
    localStorage.setItem('model_name', selectedModel); // Lưu vào localStorage
    localStorage.setItem('temperature', temperature); // Lưu vào localStorage

});
// Khôi phục giá trị khi trang tải
document.addEventListener('DOMContentLoaded', () => {
    const savedModel = localStorage.getItem('model_name');
    const savedTemperature = localStorage.getItem('temperature');

    // Nếu có giá trị đã lưu, áp dụng vào giao diện
    if (savedModel) {
        modelSelect.value = savedModel;
    } else {
        // Giá trị mặc định nếu không có trong localStorage
        localStorage.setItem('model_name', modelSelect.value);
    }

    if (savedTemperature) {
        temperatureInput.value = savedTemperature;
    } else {
        // Giá trị mặc định nếu không có trong localStorage
        localStorage.setItem('temperature', temperatureInput.value);
    }

});

function getSelectedEntities() {
    return getEntites().then(e => {
        const selectedEntities = {};

        document.querySelectorAll("#entityList .entity-item").forEach(item => {
            const select = item.querySelector("select");
            const selectedValue = select.value;
            const key = select.dataset.entity;

            const entityKeys = e[key]["entity"];

            if (selectedValue !== "None") {
                // Chuẩn bị object rule
                const rule = { method: selectedValue };

                // Lấy các input param nếu có
                const inputs = item.querySelectorAll(".param-container input");
                if (selectedValue === "mask_character" && inputs.length === 2) {
                    rule["start"] = parseInt(inputs[0].value) || 0;
                    rule["end"] = parseInt(inputs[1].value) || 0;
                } else if (
                    (selectedValue === "n_last_character" || selectedValue === "n_first_character") &&
                    inputs.length === 1
                ) {
                    rule["length"] = parseInt(inputs[0].value) || 0;
                }

                // Gán rule vào từng entity liên quan
                entityKeys.forEach(k => {
                    selectedEntities[k] = rule;
                });
            }
        });

        return selectedEntities;
    });
}