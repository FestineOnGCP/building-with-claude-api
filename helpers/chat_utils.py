# Import statements
import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

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


def chat(messages, system=None, temperature=1.0, stop_sequences=None):
    params = {
        # "model": "qwen3:4b-instruct",
        "model": "qwen2.5:3b",
        "max_tokens": 1000,
        "messages": messages,
        "extra_body": {
            "temperature": temperature
        }
    }

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

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

def generate_dataset(output_dir=None):
    prompt = """
Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
    {
        "task": "Description of task",
    },
    ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
* Focus on tasks that do not require writing much code

Please generate 3 objects.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```JSON")
    response = chat(messages, stop_sequences=["```"])

    if output_dir:
        script_dir = output_dir
    else:
        script_dir = Path(__file__).resolve().parent
    
    file_path = script_dir/"dataset.json"

    print(script_dir)
    print(file_path)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)
