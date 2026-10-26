# Import statements
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

# Import env to session and initialize anthropic
console = Console()
load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), base_url=os.getenv("BASE_URL"))

def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": text
    }
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {
        "role": "assistant",
        "content": text
    }
    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0):
    params = {
        # "model": "qwen3:4b-instruct",
        "model": "qwen2.5:3b",
        "max_tokens": 1000,
        "messages": messages,
        "extra_body": {
            "temperature": temperature
        }
    }
    print(f"list of parameters are {params}")
    if system:
        params["system"] = system

    response = client.messages.create(**params)
    for block in response.content:
        if block.type == "text":
            return block.text

def chat_stream(messages, system=None, temperature=1.0, stop_sequences=None, start_string=""):
    params = {
        "model": "qwen2.5:3b",
        "max_tokens": 1000,
        "messages": messages,
        "extra_body": {
            "temperature": temperature
        }
    }

    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
        start_stream = start_string

    full_text = start_stream
    with client.messages.stream(**params) as stream, Live(Markdown(full_text), console=console, refresh_per_second=10) as live:
        for text in stream.text_stream:
            full_text += text
            live.update(Markdown(full_text))
    return full_text
