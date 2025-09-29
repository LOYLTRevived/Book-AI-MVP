# search.py

import os
import argparse
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


def perfrom_search(query: str, collection_name: str = "knowledge_base", db_path: str = "knowledge_base_db", top_k: int = 5):
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
    return search_results

def main():
    """
    Main function to handle command-line arguments and run the search
    """
    parser = argparse.ArgumentParser(description="Search a Qdrant vector database with a text query.")
    parser.add_argument("query", help="The text query to search for.")
    parser.add_argument("--top_k", type=int, default=5, help="The number of top results to retrieve")
    args = parser.parse_args()

    print(f"Searching for '{args.query}'...")

    results = perfrom_search(args.query, top_k=args.top_k)

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