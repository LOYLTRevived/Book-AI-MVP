# extract_claims.py

"""
Documentation:

Dependencies:
Requires os, json, sys, logging, LLM functions (llm.get_llm_response), DB functions (db.insert_claim), and ingestion utilities (ingest.read_file_content, ingest.chunk_text).

Key Functionality:
This script orchestrates the process of transforming raw text into structured database entries.

    1. Claim Extraction Logic (extract_claims)
    Prompt Consistency: The LLM prompt remains a strict instruction for the model to act as a "meticulous claims extractor" and return a JSON array containing "claim_id" and "claim_text" for each extracted assertion.
    Chunking: It uses ingest.chunk_text to break the source document into manageable pieces, ensuring the text fits within the LLM's context window.

    2. Claim ID Change (Critical Update)
    UUID Removal: The script no longer generates a unique claim_id using uuid4() within the Python code.
    Reliance on DB: The extracted claim dictionary now only contains "claim_text" and "source_file". The process is now fully reliant on the db.insert_claim function to generate and assign the unique primary key ID upon insertion.

    3. Database Persistence (main())
    After successful JSON parsing of the LLM's response, the main() function iterates over the claims.
    It calls db.insert_claim(...) for each claim, passing the text, source reference, and a placeholder line_id. The DB handles assigning the unique integer claim_id and the default 'unreviewed' status.

    4. Execution (main())
    The script accepts a document path as a command-line argument, reads the text, extracts the claims in chunks, and automatically inserts them into the database.
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

