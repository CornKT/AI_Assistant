import solara
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

# Tải biến môi trường từ tệp .env
load_dotenv()

# Lấy API key từ biến môi trường
OPENTAI_API_KEY = os.getenv('OPENAI_API_KEY')
# openai.api_key = api_key
client = OpenAI()
# Tạo biến trạng thái để lưu trữ tin nhắn
messages = solara.reactive([])

# Hàm để gửi tin nhắn đến OpenAI và nhận phản hồi
def send_message_to_openai(user_message):
    try:
        print(OPENTAI_API_KEY)
        print(messages.value)
        response = client.chat.completions.create(
            messages=messages.value,
            model="gpt-4o-mini"
        )
        # Lấy phản hồi từ OpenAI
        print(response)
        return response.choices.message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Định nghĩa trang chat box
@solara.component
def Page():
    # Tạo biến trạng thái để lưu trữ tin nhắn người dùng
    user_input, set_user_input = solara.use_state("")

    # Hàm để xử lý khi gửi tin nhắn
    def handle_send():
        if user_input.strip():
            # Thêm tin nhắn của người dùng vào danh sách
            messages.value.append({"role": "user", "content": user_input})
            print(user_input)
            # Gửi tin nhắn đến OpenAI và nhận phản hồi
            response = send_message_to_openai(user_input)
            # Thêm phản hồi vào danh sách tin nhắn
            messages.value.append({"role": "assistant", "content": response})
            # Xóa nội dung trong ô nhập liệu
            set_user_input("")

    # Giao diện của ứng dụng
    solara.InputText("input", value=user_input, on_value=set_user_input)
    solara.Button(label="Send", on_click=handle_send)
    
    # Hiển thị các tin nhắn trong hộp chat
    with solara.Column(style={"min-height": "50vh"}):
        with solara.lab.ChatBox():
            for item in messages.value:
                with solara.lab.ChatMessage(user=item["role"]):
                    solara.Markdown(item["content"])
