# test_llm.py

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

