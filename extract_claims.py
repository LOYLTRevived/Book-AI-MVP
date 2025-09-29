# extract_claims.py

"""
Documentation:

Dependencies:
Requires os, json, sys, logging, uuid (for claim IDs), and functions from llm.py and db.py.

Key Functionality:
This script orchestrates the process of transforming raw text into structured database entries.

    1. Claim Extraction Logic (extract_claims(text, filename))
    Chunking: It first calls chunk_text(text) (imported from ingest.py) to break the potentially large document text into smaller, manageable pieces for the LLM.
    LLM Prompt: It loops through each text chunk and constructs a highly specific prompt. This prompt defines the role of the LLM ("meticulous claims extractor") and demands the output be a strict JSON array of objects, each containing a "claim_id" and "claim_text". This is crucial for reliable automated processing.
    LLM Call and Parsing: It calls get_llm_response(prompt) (llm.py). It then attempts to parse the raw text response using json.loads().
    Metadata Assignment: For every successfully parsed claim, it assigns:
    A unique claim_id using uuid4().
    The claim_text extracted by the LLM.
    The source_file name for citation.

    2. Persistence and Utility Functions
    save_claims_to_json(claims, output_filepath): A utility function to save the extracted claims to a local JSON file, primarily for debugging or inspection.
    Database Insertion (in main()): After all claims are extracted, the main function iterates through the final list and calls insert_claim(...) (from db.py) for each one.
    It uses a placeholder line_id="default", but the design suggests this should be used later to group related claims (e.g., claims about "Chapter 3").

    3. Execution (main())
    It accepts a document path as a command-line argument.
    It handles two types of input: a raw document (which it reads and chunks) or a JSON file of pre-chunked text.
    It prints the extracted claims and confirms the insertion of claims into the database.
"""

import os
import json
import sys
import logging
from uuid import uuid4
from llm import get_llm_response
from db import insert_claim
from ingest import read_file_content, chunk_text, save_chunks_to_json

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_claims_to_json(claims: list, output_filepath: str):
    """
    Saves a list of extracted claims to a JSON file.

    Args:
        claims (list): The list of claims to save.
        output_filepath (str): The path to the output JSON file
    """
    try:
        logging.info (f"Saving {len(claims)} claims to '{output_filepath}'...")
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(claims, f, indent=2)
        logging.info("Claims saved successfully.")
    except Exception as e:
        logging.error(f"Error saving claims to JSON: {e}")

def extract_claims(text: str, filename: str) -> list:
    """
    Prompts the LLM to extract a list of claims from a given text and fromats them with citation metadata.

    Args;
        text (str): The text content (eg, a chapter from a book).
        filename (str): The name of the file the text came from.

    Returns: 
        list: A list of dictionaries, where each dictionary represents an extracted claim
        with its citation metadata
        Example: [{"claim_id": "...", "claim_text": "...", "source_file: "..."}]
    """
    logging.info(f"Preparing prompt for claim extraction from {filename}...")

    # We now loop over chunks of text, using the Chunk_text function from ingest.py
    text_chunks = chunk_text(text)
    all_claims = []

    for i, chunk in enumerate(text_chunks):
        logging.info(f"Processing chunk {i+1}/{len(text_chunks)}...")

        prompt = f"""
You are a meticulous claims extractor. Your task is to read the following text and identify a list of distinct, self-contained claims. A claim is a single statement or assertion that can be debated or verified.

Please return your response as a JSON array of objects. Each object in the array must have two keys: "claim_id" and "claim_text". Do not include any other text or explanation in your response. The response must be a valid JSON array only.

Example of desired output:
```json
[
  {{"claim_id": "...", "claim_text": "The sky is blue due to Rayleigh scattering."}},
  {{"claim_id": "...", "claim_text": "Photosynthesis is the process used by plants to convert light energy into chemical energy."}}
]
```

Here is the text to analyze:

{chunk}
"""
        llm_raw_response = get_llm_response(prompt)

        if not llm_raw_response:
            logging.error("Failed to get a response from LLM.")
            return []
    
        try:
            claims_list = json.loads(llm_raw_response)

            for claim in claims_list:
                if "claim_text" in claim:
                    claims_with_metadata = {
                        "claim_id": str(uuid4()),
                        "claim_text": claim["claim_text"],
                        "source_file": filename
                    }
                    all_claims.append(claims_with_metadata)
    
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON from LLM response for chunk {i + 1}. Raw response was not valid JSON: {e}")
            logging.debug(f"Raw LLM response: {llm_raw_response}")
            continue

    return all_claims
    
    
def main():
    """
    Main function to test the claim extraction process on a local file.
    """
    if len(sys.argv) < 2:
        print("Usage: python extract_claims.py <path_to_document>")
        return
    
    chunk_file = sys.argv[1]
    
    if not os.path.exists(chunk_file):
        logging.error(f"Test file '{chunk_file}' not found.")
        return
    
    if chunk_file.endswith('.json'):
        with open(chunk_file, 'r', encoding='utf-8') as f:
            text_chunks = json.load(f)
    else:
        book_chapter_text = read_file_content(chunk_file)
        text_chunks = [book_chapter_text]

    # Now process each chunk to extract claims
    claims = []
    for chunk in text_chunks:
        claims.extend(extract_claims(chunk, os.path.basename(chunk_file)))

    if claims:
        print("\n--- Extracted Claims ---")
        print(json.dumps(claims, indent=2))
    # Automatically insert each claim into the database
        for claim in claims:
            insert_claim(
                line_id="default", # You can set this to a topic or group if available (but just a placeholder for now)
                claim_text=claim["claim_text"],
                source_ref=claim["source_file"]
            )
        print(f"{len(claims)} claims inserted into the database.")
    else:
        print("No claims were extracted. See logs for details.")



if __name__ == "__main__":
    main()

