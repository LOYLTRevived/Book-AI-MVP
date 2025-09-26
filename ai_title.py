# ai_title.py

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