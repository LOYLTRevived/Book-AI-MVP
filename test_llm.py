# test_llm.py

"""
Documentation:

Dependencies:
Requires os, dotenv, and the huggingface_hub.InferenceClient.

Key Functionality:
This script is purely for diagnostics and testing, separate from the primary application flow.

    1. Direct LLM Connection
    Configuration: It loads the HUGGINGFACEHUB_API_TOKEN directly and specifies the model (meta-llama/Meta-Llama-3-8B-Instruct), mirroring the setup in llm.py.
    Client Initialization: It directly instantiates the InferenceClient.

    2. Test Execution
    Prompt: It defines a simple, non-complex test prompt: "Explain why the sky looks blue in one short paragraph."
    Chat Completion: It calls client.chat_completion() using the same conversational endpoint as llm.py.
    Inference Parameters: It uses distinct inference parameters from llm.py to test different LLM behaviors:
    max_tokens=150: A shorter output limit.
    temperature=0.7: A higher temperature than the 0.3 used in the application's main code. This encourages a more creative or variable response, which is fine for a test but generally avoided for structured output (like JSON) needed by ai_title.py and extract_claims.py.
    Output: It prints the LLM's raw response to the console or displays an error if the connection fails.
"""

import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Pick a model (chat-based works better for Llama)
module_name = 'meta-llama/Meta-Llama-3-8B-Instruct'

# Set up the client
client = InferenceClient(model=module_name, token=HUGGINGFACE_API_TOKEN)

# Define a test prompt
prompt = "Explain why the sky looks blue in one short paragraph."

try:
    # Use chat endpoint since Llama models are conversational
    response= client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7  
    )

    

    print("\n--- LLM Response ---\n")
    print(response.choices[0].message["content"])

except Exception as e:
    print(f"Error: {e}")

