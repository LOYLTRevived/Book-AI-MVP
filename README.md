# Book-AI-MVP
Books + AI + Fighting = Loyl

Living Record Project Workflow
This document outlines the core workflow for the "Living Record" project, explaining how each script contributes to the overall process.

The entire workflow can be summarized in five key steps: Upload → Chunk → Embed → Store → Query.

1. Upload & Chunk (ingest.py)
This is the first step of the workflow. The ingest.py script is responsible for taking your raw reading material (in this case, a JSON file) and preparing it for the next step.

Action: You provide a file path to the script.

Purpose: It reads the file and breaks the content into smaller, manageable pieces, or "chunks."

Command: python ingest.py <your_json_file>.json

2. Embed & Store (embed.py)
Once the data is chunked, it's ready to be converted into a machine-readable format and stored in the vector database. The embed.py script handles this process.

Action: This script takes the chunks from ingest.py.

Purpose: It uses a sentence transformer model to convert each chunk into a numerical vector (the "embedding"). It then sends these vectors and their original text to the Qdrant Cloud database for storage.

Command: python embed.py <your_json_file>.json

3. Query (search.py)
This is the final step, where you can actually interact with your knowledge base. The search.py script allows you to ask questions and find relevant information.

Action: You provide a text query to the script.

Purpose: The script converts your query into a vector and uses it to find the most similar vectors (and their corresponding text chunks) in the Qdrant database.

Command: python search.py "your search query here"

Workflow at a Glance
(Your Reading Material)
      ↓
[ingest.py]
  (Upload & Chunk)
      ↓
(Text Chunks)
      ↓
[embed.py]
  (Embed & Store)
      ↓
(Vector Database)
      ↓
[search.py]
  (Query)
      ↓
(Search Results)
