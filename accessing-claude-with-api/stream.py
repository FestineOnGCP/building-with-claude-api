import helpers.common_import as ci
console = ci.Console()

messages = []
user_input = input("\033[90mPrompt:\033[0m ")
prompt = f"""
    Give a concise response to the user input:
    {user_input}
"""

while user_input.lower() != "quit":
    ci.add_user_message(messages, prompt)
    print("----------------")
    response = ci.chat_stream(messages)
    print("----------------\n")
    ci.add_assistant_message(messages, response)
    user_input = input("\033[90mPrompt:\033[0m ")
    prompt = f"""
        Give a concise response to the user input:
        {user_input}
    """

print("Thanks for using our application. Hope to see you again soon.")