from pathlib import Path
from openai import OpenAI
from astra_assistants import patch
import json
import solara
from typing import List, TypedDict


import os
from dotenv import load_dotenv

# Tải biến môi trường từ tệp .env
load_dotenv()
os.environ["ASTRA_DB_APPLICATION_TOKEN"] =  os.getenv("ASTRA_DB_APPLICATION_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# def show_json(obj):
#     display(json.loads(obj.model_dump_json()))

# def pretty_print(messages):
#     print("# Messages")
#     for m in messages.data:
#         print(m)
#         print(f"{m.role}: {m.content[0].text.value}")
#     print()



class MessageDict(TypedDict):
    role: str
    content: str

# Danh sách reactive chứa các tin nhắn
messages: solara.Reactive[List[MessageDict]] = solara.reactive([])


# def pretty_print(messages):
#     print("# Messages")
#     for m in messages.data:
#         print(m)
#         print(f"{m.role}: {m.content[0].text.value}")
#     print()

client = patch(OpenAI())

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="openai/gpt-4o-mini"
)
print(assistant)

MATH_ASSISTANT_ID = assistant.id
# print(MATH_ASSISTANT_ID)

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id)

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(MATH_ASSISTANT_ID, thread, user_input)
    return thread, run

@solara.component
def Page():
    solara.Style(Path("./static/styles.css"))

    # Biến reactive lưu tin nhắn người dùng nhập
    # user_input = solara.reactive("")  
    thinking_index = solara.reactive(None)  # Để lưu vị trí của tin nhắn "I'm thinking..."

    def send(message):
        # Thêm tin nhắn của người dùng vào danh sách
        # print(">>user_input.value: ", user_input.value)
        # user_input.value = ""
        messages.value = [
            *messages.value,
            {"role": "user", "content": message},
        ]
        print(">>>>Mes val", messages.value)
        # Gọi API OpenAI với tin nhắn của người dùng
        try:
            call_openai(message)  # Truyền message trực tiếp vào hàm call_openai
        except Exception as e:
            print(f"Error in send: {e}")

    # Task bất đồng bộ xử lý API gọi đến trợ lý AI
    def call_openai(message):
        try:
            print("Starting call_openai...")  # Kiểm tra xem hàm có được gọi không
            user_message_count = len([m for m in messages.value if m["role"] == "user"]) if messages.value else 0

            if user_message_count == 0:
                print("No user messages, exiting call_openai.")
                return
            
            # Tạo thread và gửi tin nhắn của người dùng
            print(">>Input to thread run: ", message)  # Hiển thị giá trị của tin nhắn đã được truyền vào
            thread, run = create_thread_and_run(message)
            print(">>Thread and run created.")  # Kiểm tra thread và run có được tạo không
            
            # Thêm tin nhắn trống cho AI
            messages.value = [*messages.value, {"role": "assistant", "content": "I'm thinking..."}]
            thinking_index.value = len(messages.value) - 1  # Lưu lại vị trí của tin nhắn "I'm thinking..."
            print(">>I'm thinking message added.")
            
            # Khi kết quả từ AI hoàn thành
            if run.status == "completed":
                print(">>Run completed.")  # In khi run được hoàn thành
                # Lấy phản hồi từ thread sau khi AI trả về kết quả
                response = get_response(thread)
                
                # Kiểm tra phản hồi từ AI và cập nhật nội dung
                if response and len(response.data) > 0:
                    assistant_message = response.data[0].content[0].text.value
                    if assistant_message:
                        updated_messages = messages.value[:]
                        updated_messages[thinking_index.value] = {"role": "assistant", "content": assistant_message}
                        messages.value = updated_messages  # Cập nhật lại toàn bộ messages.value
                        print(">>Assistant message updated.")
        except Exception as e:
            print(f"Error in call_openai: {e}")

    # Không cần sử dụng use_task cho call_openai vì đã truyền trực tiếp tin nhắn vào từ hàm send

    # Giao diện
    solara.lab.ThemeToggle()
    with solara.Column(style={"width": "100%", "max-height": "100%", "min-height": "70%","padding": "100px"}):
        solara.Title("CAM ON VI DA DEN!")
        with solara.Sidebar():
            solara.Markdown("## I am in the sidebar")
            solara.SliderInt(label="Ideal for placing controls")
        # solara.Info("I'm in the main content area, put your main content here")
        with solara.lab.ChatBox(
            # classes = ["my-chatbox"]
        ):
            # Hiển thị danh sách tin nhắn
            for item in messages.value:
                with solara.lab.ChatMessage(
                    user=item["role"] == "user",
                    avatar=False,
                    name="ChatGPT" if item["role"] == "assistant" else "User",
                    # classes = ["my-chatmessage"],
                    color="rgba(0,0,0, 0.06)" if item["role"] == "assistant" else "#ff991f",
                    avatar_background_color="primary" if item["role"] == "assistant" else None,
                    border_radius="20px",
                ):
                    solara.Markdown(item["content"])

        # Khung nhập tin nhắn người dùng
        solara.lab.ChatInput(
            send_callback=send,
            # style={
            #     "background-color": "#212121",  # Màu nền cụ thể
            # }
        )

