import os
import argparse
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

#Get the Qdrant Cloud credentials from enviroment variables
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


def find_similar_chunks(query_text: str, collection_name: str = "knowledge_base", top_k: int = 5):
    """
    Finds the most similar chunks to a given text query in the Qdrant collection.

    Args: 
        query_text (str): The text to find similar chunks for.
        collection_name (str): The name of the Qdrant collection.
        top_k (int): The number of top results to retrieve.

    Returns:
        list: A list of search results.
    """

    # Initialize the sentence transfomer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Initialize the Qdrant client with your cloud credentials
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )


    # Encode the new text chunk into a vector
    query_vector = model.encode(query_text).tolist()

    # Perform the search for similar vectors
    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
    )


    return search_results

def main():
    """
    Main function to handle command-line arguments and run the search.
    """
    parser = argparse.ArgumentParser(description="Find similar text chunks in a Qdrant database.")
    parser.add_argument("query", help="The text query to search for similar chunks.")
    parser.add_argument("--top_k", type=int, default=5, help="The number of top results to retrieve.")
    args = parser.parse_args()

    print(f"Finding similar chunks for: '{args.query}'...")

    results = find_similar_chunks(args.query, top_k=args.top_k)

    print("\n--- Search Results ---")
    if not results:
        print("No similar results found. Make sure you have uploaded the documents to the collection.")
    else:
        for i, result in enumerate(results):
            chunk_text = result.payload.get("chunk_text", "N/A")
            score = result.score
            print(f"\nResult {i+1} (Score: {score:.4f}):")
            print(f"Chunk Text: {chunk_text}")

if __name__ == "__main__":
    main()