# Import packages
from helpers.chat_utils import add_assistant_message, add_user_message, chat
from rich.console import Console
from rich.markdown import Markdown

# Initialize the begining of conversation
console = Console()
messages = []

# Add message to user
add_user_message(messages, "What is quantum mechanics? Give a concise response")

# Make first api request
answer = chat(messages)
console.print(Markdown(answer))

# Add assistant response
add_assistant_message(messages, answer)

# Add second user message
add_user_message(messages, "Give another sentence")

# Make final request
final_answer = chat(messages)
print()
console.print(Markdown(final_answer))
