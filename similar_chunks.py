# similar_chunks.py

"""
Documentation:

Dependencies:
Requires os, argparse, dotenv, qdrant-client, sentence-transformers, and a new, crucial dependency: synthesize.synthesize_answer.

Key Functionality:
This script's function is nearly identical to search.py, reinforcing the RAG/retrieval capability of the system.

    1. Retrieval (Finding Chunks)
    Connection and Model: Connects to Qdrant and uses the standard 'all-MiniLM-L6-v2' model.
    find_similar_chunks(query_text, collection_name, top_k): Performs semantic search, but now specifically targets the raw chunk vector store, which is defaulted to "chunks_collection" (as defined in the embed_chunks.py documentation).
    Output: Returns the raw document chunks that are semantically related to the user's query.

    2. Generation (Synthesis Integration)
    Context Preparation: In the main() function, after retrieving the chunks, the script iterates through the results. It constructs a list of dictionaries, where each dictionary represents a temporary "claim" consisting of the chunk_text and a placeholder "source_ref": "chunk".
    Synthesis Call: It calls the new synthesize_answer(args.query, chunk_claims) function. This is the critical change: the script now passes the retrieved raw chunk context directly to the LLM for synthesis, rather than simply printing the raw chunks.

    3. Output
    It first prints the raw search results (score and chunk text), providing transparency on the retrieval step.
    It then prints the final, LLM-generated Synthesized Answer based on those chunks.
"""

import os
import argparse
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from synthesize import synthesize_answer

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
    parser.add_argument("--collection", default="chunks_collection", help="Qdrant collection to search.")
    args = parser.parse_args()

    print(f"Finding similar chunks for: '{args.query}'...")

    results = find_similar_chunks(args.query, collection_name=args.collection,top_k=args.top_k)

    print("\n--- Search Results ---")
    if not results:
        print("No similar results found. Make sure you have uploaded the documents to the collection.")
    else:
        chunk_claims = []
        for i, result in enumerate(results):
            chunk_text = result.payload.get("chunk_text", "N/A")
            score = result.score
            print(f"\nResult {i+1} (Score: {score:.4f}):")
            print(f"Chunk Text: {chunk_text}")
            chunk_claims.append({"claim_text": chunk_text, "source_ref": "chunk"})
        
        # Synthesize answer from top chunks
        answer = synthesize_answer(args.query, chunk_claims)
        print("\n--- Synthesized Answer ---\n")
        print(answer)

if __name__ == "__main__":
    main()