# Import statements
import os

from anthropic import Anthropic
from dotenv import load_dotenv

# Import env to session and initialize anthropic
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


def chat(messages, model="claude-sonnet-5", max_tokens=1000):
    response = client.messages.create(
        model = model,
        max_tokens = max_tokens,
        messages = messages
    )
    for block in response.content:
        if block.type == "text":
            return block.text
