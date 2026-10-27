# Import statements
import ast
import json
import os
import re
from pathlib import Path
from statistics import mean

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

# Prompt evaluation functions

def generate_dataset(user_prompt, output_dir=None):
    """Take a user prompt describing what kind of dataset to generate and an optional destination where the file should be created"""
    prompt = user_prompt
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```JSON")
    response = chat(messages, stop_sequences=["```"])
    console.print(Markdown(f"```JSON {response} ```" ))
    if output_dir:
        script_dir = output_dir
    else:
        script_dir = Path(__file__).resolve().parent
    
    file_path = script_dir/"dataset.json"

    print(f"File Path: {file_path}")

    with file_path.open("w", encoding="utf-8") as f:
        response = json.loads(response) # Converts the returned json string to an object.
        json.dump(response, f, indent=2)

def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0

def validate_regex(text):
    try:
        re.compile(re.sub(r",\s*([\]}])", r"\1", text.strip()))
        return 10
    except re.error:
        return 0

def grade_by_code(test_case, output):
    if test_case["format"] == "python":
        return validate_python(output)
    elif test_case["format"] == "json":
        return validate_json(output)
    elif test_case["format"] == "regex":
        return validate_regex(output)
    else:
        return 0
    

def run_prompt(test_case):
    """Take in a test case, input it into the prompt, and call Claude to execute this prompt"""

    prompt = f"""
        Please, solve the following task:
        The task to be completed
        <task>
        {test_case["task"]}
        </task>

        The format which you should return the solution as:
        <format>
        {test_case["format"]}
        </format>

        Adhere to the below solution criteria when providing the solution:
        <solution_criteria>
        {test_case["solution_criteria"]}
        </solution_criteria>

        * Respond only with Python, JSON, or a regular expression code block.
        * For the json and regex task, do not give me their python implementation. Just the their code block response is needed.
        * For the python task, give me the python implementation code block.
        * Do not add any comments or commentary or explanation.
    """
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```code")
    output = chat(messages, stop_sequences=["```"])

    return output

def grade_by_model(test_case, model_output):
    """Takes both the test case and the output from the model. Define the evaluation criteria and infuse this parameters into it.
    Then, send this evaluation criteria to Claude to grade the quality of the score.
    """

    eval_prompt = f"""
        You are an expert code reviewer. Evaluate this AI-generated solution.
        
        Task to be completed: 
        <task>
        {test_case["task"]}
        </task>

        Solution for the task to evaluate:
        <solution>
        {model_output}
        </solution>

        Solution Criteria to be considered when evaluating the solution against the task:
        <solution_criteria>
        {test_case["solution_criteria"]}
        </solution_criteria>

        * Do not use double quotes inside string values. Use single quotes instead, and do not include line breaks inside strings.
        
        Provide your evaluation as a structured JSON object with:
        - "strengths": An array of 1-3 key strengths
        - "weaknesses": An array of 1-3 key areas for improvement  
        - "reasoning": A concise explanation of your assessment
        - "score": A number between 1-10
    """

    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    eval_result = chat(messages, stop_sequences=["```"])
    # eval_result = re.sub(r",\s*([\]}])", r"\1", eval_result.strip())
   
    return json.loads(eval_result, strict=False)

def eval_test_case(test_case):
    """Calls the run_prompt() to get a test case Claude output, Grade this output, and return the result set"""

    output = run_prompt(test_case)

    # Grade by model result
    eval_result = grade_by_model(test_case, output)
    model_score = eval_result["score"]
    model_reasoning = eval_result["reasoning"]
    prompt_strengths = eval_result["strengths"]

    # Grade by code results
    code_score = grade_by_code(test_case, output)
    print(code_score)
    score = (model_score + code_score) / 2
    # eval_result = json.loads(eval_result)
    result = {
        "output": output,
        "score": score,
        "reasoning": model_reasoning,
        "strengths": prompt_strengths,
        "test_case": test_case["task"]
    }

    return result

def run_eval(dataset):
    """This goes through all the items on a dataset and calls the eval_test_case() for each of the test case defined within
    the dataset"""

    results = []

    for test_case in dataset:
        result = eval_test_case(test_case)
        results.append(result)

    average_score = mean([result["score"] for result in results])

    print(f"\nThe average score for the prompt is {average_score}\n")

    return results
