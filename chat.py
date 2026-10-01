from helpers.chat_utils import add_assistant_message, add_user_message, chat
from rich.console import Console
from rich.markdown import Markdown

# Initialize message size
default = " Give a concise response"
messages = []
console = Console()
print("\n")
response = input("\033[90mAsk any question:\033[0m ")
response += default

# Run a while loop to request message
while response != "Quit" + default:
    add_user_message(messages, response)
    model_response = chat(messages)
    print("----------------")
    console.print(Markdown(model_response))
    add_assistant_message(messages, model_response)
    print("----------------\n")
    response = input("\033[90mAsk any question:\033[0m ")
    response += default
