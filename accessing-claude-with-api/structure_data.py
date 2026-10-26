import helpers.common_import as ci

console = ci.Console()

# EventBridge example
messages = []
print("----------------------------\nEventBridge example\n----------------------------")
start_stream = "```json"
ci.add_user_message(messages, "Generate a very short event bridge rule as json")
ci.add_assistant_message(messages, start_stream)
ci.chat_stream(messages, stop_sequences=["```"], start_string=start_stream)

# AWS cli example
print("----------------------------\nAWS CLI commands example\n----------------------------")
start_stream = "```sh"
ci.add_user_message(messages, "Generate three different sample AWS CLI commands. Each should be very short")
ci.add_assistant_message(messages, start_stream)
response = ci.chat_stream(messages, stop_sequences=["```"], start_string=start_stream)
# print(f"--------------\n{response}")