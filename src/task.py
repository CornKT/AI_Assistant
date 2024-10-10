from pathlib import Path
from openai import OpenAI
from astra_assistants import patch
import solara
from typing import List, TypedDict
from matplotlib.figure import Figure
import io
from PIL import Image
from solara.lab import task

import os
from dotenv import load_dotenv

# Tải biến môi trường từ tệp .env
load_dotenv()

os.environ["ASTRA_DB_APPLICATION_TOKEN"] =  os.getenv("ASTRA_DB_APPLICATION_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

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
print(MATH_ASSISTANT_ID)

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


@task
def call_openai(message):
    # print(">>>>>>>>>>>>>>>>CALL<<<<<<<<<<<<<<<<")
    call_openai.progress = 0

    try:
        print("Starting call_openai...")  # Kiểm tra xem hàm có được gọi không
        if message == "":
            return
        call_openai.progress = 10
        thread, run = create_thread_and_run(message)
        call_openai.progress = 40
        print(">>Thread and run created.")  # Kiểm tra thread và run có được tạo không
        if run.status == "completed":
            print(">>Run completed.")  # In khi run được hoàn thành
            # Lấy phản hồi từ thread sau khi AI trả về kết quả
            response = get_response(thread)
            print(">> res: ",response)
            call_openai.progress = 70
            # Kiểm tra phản hồi từ AI và cập nhật nội dung
            if response and len(response.data) > 0:
                assistant_message = response.data[0].content[0].text.value
                if assistant_message:
                    messages.value = [*messages.value, {"role": "assistant", "content": assistant_message}]
                    print(">>Assistant message updated.")
                    # print(">>>Res: ",assistant_message)
                    # print(">>>Updated:", messages.value)
                    call_openai.progress = 100
        print(">>>end call")
    except Exception as e:
        print(f"Error in call_openai: {e}")
        return
    
# user_message_count = solara.reactive(len([m for m in messages.value if m["role"] == "user"]))

@solara.component
def MyChatbox():
    print(">>>chatboxcall")
    with solara.lab.ChatBox():
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
    print("<<<<end chatbox")
def send(message):
    print(">>>>>>>>>>>>>>>>SEND<<<<<<<<<<<<<<<<")

    # Thêm tin nhắn của người dùng vào danh sách
    messages.value = [
        *messages.value,
        {"role": "user", "content": message},
    ]
    print("Updated message value in send")
    # print(">>>>Mes val", message)
    call_openai(message)
    print("<<<<<<<<end send")
@solara.component
def Page():
    solara.Style(Path("./static/styles.css"))
    print(">>>>>>>>PAGELOAD<<<<<<<<<<<")
    # print(">>Count before: ", user_message_count)
    # print("first message: ", messages.value)
    # Biến reactive lưu tin nhắn người dùng nhập
    # Giao diện
    with solara.AppBar():
        solara.lab.ThemeToggle()
    with solara.Sidebar():
            solara.Markdown("## I am in the sidebar")
            solara.SliderInt(label="Ideal for placing controls")
    with solara.Column(style ={"height": "90vh","width": "100%", "margin": "7%", "padding": "10px","overflow":"hidden"}):
        solara.Title("Assistant")
        solara.Info("I'm in the main content area, put your main content here")
        MyChatbox()
        solara.ProgressLinear(call_openai.progress if call_openai.pending else False)
        if call_openai.pending:
            solara.Text("I'm thinking...", style={"font-size": "1rem", "padding-left": "20px"})

        # Khung nhập tin nhắn người dùng
        solara.lab.ChatInput(
                send_callback=send, 
                disabled=call_openai.pending,
                style = {"bottom": "0","padding": "10px" ,"height":"20%","padding-bottom": "50px", "width": "100%"},
            )            
@solara.component
def Layout(children):
    dark_effective = solara.lab.use_dark_effective()
    return solara.AppLayout(children=children, toolbar_dark=dark_effective, color=None)