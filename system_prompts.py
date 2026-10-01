# Include helper functions
import helpers.common_import as ci

console = ci.Console()

# Create a system prompt for a Principal Refactoring Engineer
system_prompt_1 = """
You are a Strict Software Architect or a Principal Refactoring Engineer.
Use precise constraint-based system prompts (such as Robert C. Martin's Clean Code heuristics)
to write clean and DRY (Don't Repeat Yourself) code.
"""

system_prompt_2 = """
You are a Strict Software Architect or a Principal Refactoring Engineer.
Use precise constraint-based system prompts (such as Robert C. Martin's Clean Code heuristics)
to write clean and DRY (Don't Repeat Yourself) code. I only want the code without unnecessary code comment.
"""

system_prompt_3 = """
Act as a Principal Software Engineer obsessed with clean code and the DRY principle. 
Write concise, modular, and highly readable code. Eliminate all code duplication. 
Keep functions short (under 20 lines), limit arguments to three or fewer, use descriptive names, and omit redundant comments. 
If a pattern already exists in the context, reuse it instead of inventing a new one
"""

# Create initial message block
messages = []

# Add user input to messages
ci.add_user_message(messages, "Write a python function that checks a string for duplicate characters")

# Call chat function
answer = ci.chat(messages, system_prompt_2)

# Add response to messages
ci.add_assistant_message(messages, answer)

# Display returned function
console.print(ci.Markdown(answer))