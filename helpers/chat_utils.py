# Import statements
import json
import os
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

def run_prompt(test_case):
    """Take in a test case, input it into the prompt, and call Claude to execute this prompt"""

    prompt = f"""
        Please, solve the following task:
        {test_case["task"]}
    """
    messages = []
    add_user_message(messages, prompt)
    output = chat(messages)

    return output

def grade_by_model(test_case, model_output):
    """Takes both the test case and the output from the model. Define the evaluation criteria and infuse this parameters into it.
    Then, send this evaluation criteria to Claude to grade the quality of the score.
    """

    eval_prompt = f"""
        You are an expert code reviewer. Evaluate this AI-generated solution.
        
        Task: {test_case["task"]}
        Solution: {model_output}
        
        Provide your evaluation as a structured JSON object with:
        - "strengths": An array of 1-3 key strengths
        - "weaknesses": An array of 1-3 key areas for improvement  
        - "reasoning": A concise explanation of your assessment
        - "score": A number between 1-10
    """

    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```JSON")
    eval_result = chat(messages, stop_sequences=["```"])

    return eval_result

def eval_test_case(test_case):
    """Calls the run_prompt() to get a test case Claude output, Grade this output, and return the result set"""

    output = run_prompt(test_case)

    # Grade by model result
    eval_result = grade_by_model(test_case, output)
    eval_result = json.loads(eval_result)
    
    # eval_result = json.loads(eval_result)
    result = {
        "output": output,
        "score": eval_result["score"],
        "reasoning": eval_result["reasoning"],
        "strengths": eval_result["strengths"],
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
