"""
# Chatbot

A way to create a chatbot using OpenAI's GPT-4 API, utilizing their new API, and the streaming feature.
"""

import os
from typing import List

from openai import OpenAI
from typing_extensions import TypedDict

import solara
import solara.lab


class MessageDict(TypedDict):
    role: str
    content: str


if os.getenv("OPENAI_API_KEY") is None and "OPENAI_API_KEY" not in os.environ:
    openai = None
else:
    openai = OpenAI()
    openai.api_key = os.getenv("OPENAI_API_KEY")  # type: ignore

messages: solara.Reactive[List[MessageDict]] = solara.reactive([])


def no_api_key_message():
    messages.value = [
        {
            "role": "assistant",
            "content": "No OpenAI API key found. Please set your OpenAI API key in the environment variable `OPENAI_API_KEY`.",
        },
    ]


def add_chunk_to_ai_message(chunk: str):
    print(">>>Chunk")
    messages.value = [
        *messages.value[:-1],
        {
            "role": "assistant",
            "content": messages.value[-1]["content"] + chunk,
        },
    ]
    print("<<<<end chunk")


@solara.component
def Page():
    print(">>>>>PAGELOAD<<<<<")
    user_message_count = len([m for m in messages.value if m["role"] == "user"])

    def send(message):
        print(">>>>>SEND")
        messages.value = [
            *messages.value,
            {"role": "user", "content": message},
        ]
        print("<<<<<<end send")


    def call_openai():
        print(">>>>>CALL")
        if user_message_count == 0:
            return
        if openai is None:
            no_api_key_message()
            return
        print("<mesval>: ", messages.value)
        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages.value,  # type: ignore
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].finish_reason == "stop":  # type: ignore
                return
            add_chunk_to_ai_message(chunk.choices[0].delta.content)  # type: ignore
        print("<<<<<end call")
    task = solara.lab.use_task(call_openai, dependencies=[user_message_count])  # type: ignore
    with solara.Column(
        style={"width": "700px", "height": "50vh"},
    ):
        with solara.lab.ChatBox():
            for item in messages.value:
                with solara.lab.ChatMessage(
                    user=item["role"] == "user",
                    avatar=False,
                    name="ChatGPT" if item["role"] == "assistant" else "User",
                    color="rgba(0,0,0, 0.06)" if item["role"] == "assistant" else "#ff991f",
                    avatar_background_color="primary" if item["role"] == "assistant" else None,
                    border_radius="20px",
                ):
                    solara.Markdown(item["content"])
        if task.pending:
            solara.Text("I'm thinking...", style={"font-size": "1rem", "padding-left": "20px"})
        solara.lab.ChatInput(send_callback=send, disabled=task.pending)
        