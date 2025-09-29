# search.py

"""
Documentation:

Dependencies:
Requires os, argparse, dotenv, qdrant-client, and sentence-transformers.

Key Functionality:
This script is the main retrieval mechanism for the knowledge base, allowing users to find source material relevant to a question or claim.

    1. Function Name Change
    The primary search function was renamed from the original perfrom_search to the clearer and more consistent semantic_search(query, collection_name, top_k).

    2. Return Value Modification (Critical Change)
    The semantic_search function's return logic was changed to extract and only return the payload (a list of dictionaries) from the Qdrant search results. It no longer returns the complete Qdrant result object which included the score and full metadata.

    3. Execution (main()) — Logic Bug Introduced
    The main() function is now logically inconsistent and contains a bug. Because semantic_search no longer returns the full result objects, the code in main() that attempts to access result.score and access payload data via result.payload.get(...) will fail.
    If this script is run standalone, it will likely crash because the dictionary returned by semantic_search (the payload) does not have a .score attribute.

    4. Intended Use
    When used by the RAG orchestrator (helper.py), the script's output (a list of claim payloads containing claim_id) is precisely what is needed for the database filtering step. However, the standalone main() function should be corrected to handle the new return structure or revert the function's internal return logic.
"""

import os
import argparse
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


def semantic_search(query: str, collection_name: str = "knowledge_base", top_k: int = 5):
    """
    Performs a semantic search on the Qdrant collection.

    Args:
        query (str): The search query text.
        collection_name (str): The name of the Qdrant collection.
        top_k (int): The number of top results to retrieve.

    Returns:
        list: A list of search results.
    """

    # Initialize the sentence transformer model (must be the same one as in embed.py)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Initialize the Qdrant client in memory mode
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

    # Encode the query text into a vector
    query_vector = model.encode(query).tolist()

    #Perform the search
    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
    )
    return [result.payload for result in search_results]

def main():
    """
    Main function to handle command-line arguments and run the search
    """
    parser = argparse.ArgumentParser(description="Search a Qdrant vector database with a text query.")
    parser.add_argument("query", help="The text query to search for.")
    parser.add_argument("--top_k", type=int, default=5, help="The number of top results to retrieve")
    args = parser.parse_args()

    print(f"Searching for '{args.query}'...")

    results = semantic_search(args.query, top_k=args.top_k)

    print("\n--- Search Results ---")
    if not results:
        print("No results found.")
    else:
        for i, result in enumerate(results):
            chunk_text = result.payload.get("chunk_text", "N/A")
            score = result.score
            print(f"\nResult {i+1} (Score: {score:.4f}):")
            print(f"Chunk Text: {chunk_text}")

if __name__=="__main__":
    main()