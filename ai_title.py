# ai_title.py

"""
Documentation for ai_title.py:

Dependencies: Requires the external llm.get_llm_response function (from llm.py) and standard Python sys.

Key Functionality:
    The main function is generate_title_and_description(text).
    Prompt Construction: It creates a prompt that instructs the LLM to generate a title (max 50 words) and a description.
    Input Limiting: It truncates the input text to the first 2000 characters before sending it to the LLM. This is a crucial step to manage prompt size and cost.
    Required Output Format: It strictly instructs the LLM to return the response as a JSON object with the keys 'title' and 'description'.
    LLM Call: It calls the get_llm_response(prompt) function to interact with the LLM.
    Execution (if __name__ == "__main__":):
    It reads the entire input text from sys.stdin.read(). This means the script is intended to receive its document text via piping or as a subprocess input, as seen in ingest.py.
    It prints the raw LLM output (the JSON string) to stdout.
"""

import sys
from llm import get_llm_response

def generate_title_and_description(text):
    prompt = (
        "Given the following document text, generate a concise title (max 50 words) suitable for organizing and categorizing the document."
        "Return your response as a JSON object with 'title' and 'description' keys. Only output valid JSON. \n\n"
        f"Document:\n{text[:2000]}..."  # Limit to first 2000 characters for prompt size
    )
    response = get_llm_response(prompt)
    return response

if __name__ == "__main__":
    input_text = sys.stdin.read()
    result = generate_title_and_description(input_text)
    print(result)