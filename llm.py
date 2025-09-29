# llm.py

"""
Documentation:

Dependencies:
	Requires os, logging, dotenv, and the huggingface_hub.InferenceClient.


Key Functionality:
The script defines the core mechanism for sending prompts to a remote LLM and retrieving structured text responses.

    1. Configuration and Connection
    Environment Variable: It requires and checks for the HUGGINGFACEHUB_API_TOKEN from the .env file to authenticate with the Hugging Face API.
    Client Initialization: The InferenceClient is initialized with a specific model, defaulting to meta-llama/Meta-Llama-3-8B-Instruct.

    2. get_llm_response(prompt, model_name)
    The LLM Gateway: This is the single function used by the entire codebase to communicate with the AI.
    Chat Completion Endpoint: It specifically uses the client.chat_completion method, which is generally better suited for conversational and instruction-tuned models like Llama.
    System Settings (Inference Parameters):
    max_tokens=500: The output length is set relatively high to accommodate the long-form JSON output required by extract_claims.py.
    temperature=0.3: The temperature is set low to encourage deterministic, structured, and factual responses, which is essential when expecting valid JSON output for titles and claim extraction.
    Output: It returns the text content of the LLM's response. It includes error handling to return an empty string if the connection or API call fails.

    3. Execution (main())
    Contains a test case to demonstrate the function by sending a simple query ("Explain why the sky looks blue...") and printing the response.
"""

import os
import logging
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Configure logging to see what's happening
load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def get_llm_response(prompt: str, model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct") -> str:
    """
    Connects to a Hugging Face LLM ande returns a response for a given prompt.

    Args: 
        prompt (str): The text prompt to send to the LLM.
        model_name (str): The name of the Hugging Face model to use.

    Returns: 
        str: The LLM's text response.
    """
    if not HUGGINGFACE_API_TOKEN:
        logging.error("HUGGINGFACEHUB_API_TOKEN not found. Please check your .env file")
        return ""
    
    try:
        logging.info(f"Connecting to LLM: {model_name}")
        client = InferenceClient(model=model_name, token=HUGGINGFACE_API_TOKEN)

        # Use chat endpoint for conversational models
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500, # Increase tokens from 150 to 500 for claim extraction
            temperature=0.3 # Lower temp for more structured output
        )

        return response.choices[0].message["content"]
    
    except Exception as e:
        logging.error(f"An error occured while calling the LLM: {e}")
        return ""
    
def main():
    """
    Main function to test the get_llm_response function.
    """
    # Define a test prompt
    prompt = "Explain why the sky looks blue in one short paragraph."

    print(f"Sending prompt to LLM '{prompt}'")
    response_text = get_llm_response(prompt)

    if response_text:
        print ("\n--- LLM Response --")
        print(response_text)
    else:
        print("Failed to get a response from the LLM.")

if __name__ == "__main__":
    main()