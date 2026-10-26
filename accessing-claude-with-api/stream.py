import helpers.common_import as ci
console = ci.Console()

messages = []
ci.add_user_message(messages, "What is quantum computing?")
response = ci.chat_stream(messages)

ci.add_assistant_message(messages, response)
print ("---------/n")
ci.add_user_message(messages, "Give another one sentence")
final_response = ci.chat_stream(messages)