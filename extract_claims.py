import os
import json
import logging
from uuid import uuid4
from llm import get_llm_response
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

    # Replace this with the path to your book or article
    test_file_path = "C:\\Users\\holla\\Downloads\\1-3 Earthship.pdf"
    # test_file_path = "path/to/your/document.pdf"
    # test_file_path = "path/to/your/document.docx"
    # test_file_path = "path/to/your/document.epub"
    
    if not os.path.exists(test_file_path):
        logging.error(f"Test file '{test_file_path}' not found. Please create it and add text or a PDF.")
        return
    
    book_chapter_text = read_file_content(test_file_path)

    if not book_chapter_text:
        logging.warning("Test file is empty or could not be read. Please check the file contents.")
        return
    
    # Chunk the text and save the chunks to a file
    text_chunks = chunk_text(book_chapter_text)
    base_name = os.path.splitext(os.path.basename(test_file_path))[0]
    chunks_output_file = f"{base_name}_chunks.json"
    save_chunks_to_json(text_chunks, chunks_output_file)
    
    print(f"Extracting claims from '{test_file_path}'...")
    claims = extract_claims(book_chapter_text, os.path.basename(test_file_path))

    if claims:
        print("\n--- Extracted Claims ---")
        print(json.dumps(claims, indent=2))
    else:
        print("No claims were extracted. See logs for details.")

if __name__ == "__main__":
    main()

