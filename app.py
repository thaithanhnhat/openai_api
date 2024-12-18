from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import openai
import time
import webbrowser
from threading import Timer
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Thêm API key ở đây
openai.api_key = "API-KEY"

# Lưu lịch sử hội thoại
conversation_history = [
    {
        "role": "system",
        "content": (
            "<THis your requỉe>"
        )
    }
   
]

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Chat với AI</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
    <style>
        :root {
            --background-color: linear-gradient(135deg, #f0f2f5, #c9d6ff);
            --header-color: #007bff;
            --user-message-color: #d1e7dd;
            --ai-message-color: #f8d7da;
            --button-color: #007bff;
            --font-family: 'Arial, sans-serif';
        }
        body {
            background: var(--background-color);
            font-family: var(--font-family);
            transition: background 0.3s, color 0.3s;
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }
        #chat-container {
            width: 100%;
            max-width: 600px;
            height: 80vh;
            display: flex;
            flex-direction: column;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        header {
            background-color: var(--header-color);
            color: white;
            padding: 10px;
            text-align: center;
            transition: background-color 0.3s;
            font-size: 1.5em;
            font-weight: bold;
        }
        #messages {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            list-style-type: none;
            animation: fadeIn 1s ease-in-out;
        }
        .message {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            max-width: 60%;
            animation: slideIn 0.5s ease-out;
        }
        .user-message {
            background-color: var(--user-message-color);
            align-self: flex-end;
            transition: background-color 0.3s;
        }
        .ai-message {
            background-color: var(--ai-message-color);
            align-self: flex-start;
            transition: background-color 0.3s;
        }
        #form {
            display: flex;
            padding: 10px;
            background-color: #f8f9fa;
        }
        #input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
        }
        button {
            margin-left: 10px;
            padding: 10px 20px;
            background-color: var(--button-color);
            color: white;
            border: none;
            border-radius: 4px;
            transition: background-color 0.3s, transform 0.2s;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
            transform: scale(1.05);
        }
        #chat-info {
            text-align: center;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #555;
        }
        pre, code {
            background-color: #333;
            color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }
        #theme-selector {
            padding: 5px;
            border-radius: 5px;
            border: 1px solid #ced4da;
            background-color: #f8f9fa;
            transition: background-color 0.3s, border-color 0.3s;
            cursor: pointer;
        }
        #theme-selector:hover {
            background-color: #e2e6ea;
            border-color: #adb5bd;
        }
        #theme-selector:focus {
            outline: none;
            border-color: #007bff;
        }
        .theme-option {
            padding: 10px;
            display: flex;
            align-items: center;
        }
        .theme-option img {
            width: 20px;
            height: 20px;
            margin-right: 10px;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {
            var socket = io();
            var form = document.getElementById('form');
            var input = document.getElementById('input');
            var messages = document.getElementById('messages');

            form.addEventListener('submit', function(e) {
                e.preventDefault();
                if (input.value) {
                    var userItem = document.createElement('li');
                    userItem.textContent = input.value;
                    userItem.className = 'message user-message';
                    messages.appendChild(userItem);

                    var loadingItem = document.createElement('li');
                    loadingItem.className = 'message ai-message';
                    loadingItem.innerHTML = '<div class="spinner-border" role="status"></div>';
                    messages.appendChild(loadingItem);

                    socket.emit('user_message', {data: input.value});
                    input.value = '';
                }
            });

            socket.on('response', function(msg) {
                var loadingItem = messages.querySelector('.ai-message .spinner-border').parentElement;
                loadingItem.innerHTML = formatMessage(msg.data);
                window.scrollTo(0, document.body.scrollHeight);
            });

            function formatMessage(message) {
                // Escape HTML special characters
                message = message.replace(/&/g, "&amp;")
                                 .replace(/</g, "&lt;")
                                 .replace(/>/g, "&gt;")
                                 .replace(/"/g, "&quot;")
                                 .replace(/'/g, "&#039;");
                // Wrap code blocks in <pre><code>
                return message.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
            }

            // Theme selection logic
            var themeSelector = document.getElementById('theme-selector');
            var blinkInterval;
            themeSelector.addEventListener('change', function() {
                clearInterval(blinkInterval); // Clear any existing interval
                switch (this.value) {
                    case 'light':
                        document.documentElement.style.setProperty('--background-color', 'linear-gradient(135deg, #f0f2f5, #c9d6ff)');
                        document.documentElement.style.setProperty('--header-color', '#007bff');
                        document.documentElement.style.setProperty('--user-message-color', '#d1e7dd');
                        document.documentElement.style.setProperty('--ai-message-color', '#f8d7da');
                        document.documentElement.style.setProperty('--button-color', '#007bff');
                        document.documentElement.style.setProperty('--font-family', 'Arial, sans-serif');
                        break;
                    case 'dark':
                        document.documentElement.style.setProperty('--background-color', 'linear-gradient(135deg, #333, #111)');
                        document.documentElement.style.setProperty('--header-color', '#444');
                        document.documentElement.style.setProperty('--user-message-color', '#555');
                        document.documentElement.style.setProperty('--ai-message-color', '#666');
                        document.documentElement.style.setProperty('--button-color', '#777');
                        document.documentElement.style.setProperty('--font-family', 'Courier New, monospace');
                        break;
                    case 'colorful':
                        document.documentElement.style.setProperty('--background-color', 'linear-gradient(135deg, #ffefd5, #ffe4e1)');
                        document.documentElement.style.setProperty('--header-color', '#ff69b4');
                        document.documentElement.style.setProperty('--user-message-color', '#ffdab9');
                        document.documentElement.style.setProperty('--ai-message-color', '#ffe4e1');
                        document.documentElement.style.setProperty('--button-color', '#ff4500');
                        document.documentElement.style.setProperty('--font-family', 'Comic Sans MS, cursive');
                        break;
                    case 'blinking':
                        blinkInterval = setInterval(() => {
                            let currentColor = getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim();
                            document.documentElement.style.setProperty('--background-color', currentColor === '#ffffff' ? '#000000' : '#ffffff');
                        }, 100); // Change every 100ms for faster blinking
                        document.documentElement.style.setProperty('--header-color', '#ff0000');
                        document.documentElement.style.setProperty('--user-message-color', '#00ff00');
                        document.documentElement.style.setProperty('--ai-message-color', '#0000ff');
                        document.documentElement.style.setProperty('--button-color', '#ff00ff');
                        document.documentElement.style.setProperty('--font-family', 'Impact, sans-serif');
                        break;
                }
            });
        });
    </script>
</head>
<body>
    <div id="chat-container">
        <header>Model: GPT-4o-mini</header>
        <div id="chat-info">
            <label for="theme-selector">Chọn theme:</label>
            <select id="theme-selector">
                <option value="light" class="theme-option">Sáng</option>
                <option value="dark" class="theme-option">Tối</option>
                <option value="colorful" class="theme-option">Màu sắc</option>
                <option value="blinking" class="theme-option">Chói sáng</option>
            </select>
        </div>
        <ul id="messages" class="list-group d-flex flex-column"></ul>
        <form id="form" action="">
            <input id="input" autocomplete="off" class="form-control" placeholder="Nhập tin nhắn..." />
            <button class="btn btn-primary">Gửi</button>
        </form>
    </div>
</body>
</html>'''  # Trả về nội dung HTML

@socketio.on('user_message')
def handle_user_message(json):
    user_input = json['data']

    # Thêm câu hỏi vào lịch sử hội thoại
    conversation_history.append({"role": "user", "content": user_input})

    # Gọi OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            stream=True
        )
        full_response = ""
        for chunk in response:
            if "choices" in chunk and chunk["choices"][0]["delta"].get("content"):
                content = chunk["choices"][0]["delta"]["content"]
                full_response += content
        conversation_history.append({"role": "assistant", "content": full_response})
        emit('response', {'data': full_response})
    except openai.error.RateLimitError as e:
        print(f"Lỗi: {e}")
        emit('response', {'data': "Xài bản free thì hỏi ít thôi, đợi 20 giây rồi gửi lại hoặc bơm tiền mua gói vip."})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Sử dụng Timer để mở trình duyệt sau khi server đã khởi động
    Timer(1, open_browser).start()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
