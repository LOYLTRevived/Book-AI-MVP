# similar_chunks.py

"""
Documentation:

Dependencies:
Requires os, argparse, dotenv, qdrant-client, and sentence-transformers.

Key Functionality:
This script's function is nearly identical to search.py, reinforcing the RAG/retrieval capability of the system.

    1. Configuration and Model Setup
    Qdrant Connection: It uses the QDRANT_URL and QDRANT_API_KEY from environment variables to establish a connection to the vector database.
    Model Consistency: It initializes the 'all-MiniLM-L6-v2' Sentence Transformer model, which is essential for encoding the query text into a vector that matches the space of the stored document vectors.

    2. find_similar_chunks(query_text, collection_name, top_k)
    Vectorization: It encodes the input query_text into a vector representation.
    Qdrant Search: It calls client.search() to query the vector database:
    It looks for vectors closest to the query_vector.
    It retrieves the top_k (defaulting to 5) results based on cosine similarity.
    Output: It returns the list of similar search_results, which include the chunk text and the similarity score.

    3. Distinction from search.py
    While functionally the same, this script's name (similar_chunks) better reflects its use case: finding semantically related text portions within the document corpus, which is a common pattern in building custom knowledge bases.

    4. Execution (main())
    It takes the query text as a required command-line argument.
    It prints the retrieved results, including the similarity score and the chunk text.
"""

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