#ingest.py

"""
Documentation:

Dependencies:
Requires os, json, argparse, sys, re, and several libraries for file parsing (pdfplumber, ebooklib, bs4, langchain.text_splitter). It also requires the external ai_title.py script.

Key Functionality:
This script is the main workhorse for preparing documents for the knowledge base.

    1. File Reading Functions
    The script provides specific readers for different file types:
    read_text_file(filepath): Reads plain .txt files.
    read_pdf_file(filepath): Uses pdfplumber to extract text from PDF documents.
    read_epub_file(filepath): Uses ebooklib and BeautifulSoup to parse EPUB content and strip HTML tags to get clean text.
    read_file_content(filepath): A dispatcher function that calls the appropriate reader based on the file extension.

    2. Text Processing and Chunking
    chunk_text(text, chunk_size=500, chunk_overlap=50): Uses the RecursiveCharacterTextSplitter from LangChain to divide the large document text into smaller chunks. This is critical for fitting content into the context window of LLMs and for effective vector search.
    save_chunks_to_json(chunks, output_filepath): Saves the resulting list of text chunks to a JSON file, typically named [title]_chunks.json.

    3. Metadata Generation
    get_ai_title_and_description(text): This function is key. It executes ai_title.py as a subprocess and pipes the document text to its standard input (stdin). It captures the JSON output (title and description) from the subprocess's standard output (stdout) and parses it.

    4. Execution (main())
    It takes a filename as a command-line argument.
    It reads the file and calls get_ai_title_and_description().
    It uses the generated AI title (or the original filename as a fallback) to create a sanitized filename for output.
    It executes the chunk_text function.
    It saves the list of chunks to a JSON file (e.g., data/Document Title_chunks.json).
    It saves the AI-generated title and description to a separate metadata JSON file (e.g., data/Document Title_metadata.json).
"""

import os
import json
import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ebooklib import epub
from bs4 import BeautifulSoup 
import subprocess
import pdfplumber
import sys
import re

def sanitize_filename(name):
    # Remove or replace invalid filename characters: \ / : * ? " < > | 
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def read_text_file(filepath):
    """
    Reads a plain text file from the specified filepath.
    
    Args:
        Filepath (str): The path to the text file.
    
    Returns:
        str: The content of the file as a single string
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{filepath}'was not found")
        return None
    except Exception as e:
        print(f"An error has occured while reading the file: {e}")
        return None
    
def read_pdf_file(filepath):
    """
    Reads a PDF file and extracts all text
    """
    try:
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"An error occured while reading the PDF: {e}")
        return None
    

def read_epub_file(filepath):
    """
    Reads an EPUB file and extracts all text content
    """
    try:
        book = epub.read_epub(filepath)
        text = ""
        for item in book.get_items():
            if item.get_type() == epub.ITEM.DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text += soup.get_text() + "\n"
        return text
    except Exception as e:
        print(f"An error has occured while reading EPUB: {e}")
        return None
    

def read_file_content(filepath):
    """
    Reads content from various file types based on the extension.
    """
    file_extension = os.path.splitext(filepath)[1].lower()
    if file_extension == '.txt':
        return read_text_file(filepath)
    if file_extension == '.pdf':
        return read_pdf_file(filepath)
    if file_extension == '.epub':
        return read_epub_file(filepath)
    else:
        print(f"Unsupported file type: {file_extension}")
        return None
        

    
def chunk_text(text, chunk_size=500, chunk_overlap=50):
    """
    Splits a given test into smaller, overlapping chunks.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum size of each chunk in tokens.
        chunk_overlap (int): The number of tokens to overlap between chunks.

    Returns:
        list: A list of text chunks (strings).
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)

def save_chunks_to_json(chunks, output_filepath):
    """
    Saves a list of text chuncks to a Json file.

    Args:
        Chunks (list): A list of text chunks (strings).
        output_filepath (str): The path where the Json file will be saved
    """
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=4)
        print(f"Chunks successfully saved to '{output_filepath}'")
    except Exception as e:
        print(f"An error occurred while saving the chunks: {e}")

def get_ai_title_and_description(text):
    process = subprocess.Popen(
        [sys.executable, "ai_title.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    
    stdout, stderr = process.communicate(input=text)
    if process.returncode != 0:
        print(f"Error running ai_title.py: {stderr}")
        return None, None
    try:
        result = json.loads(stdout)
        return result.get("title"), result.get("description")
    except Exception as e:
        print(f"Error parsing JSON from ai_title.py output: {e}")
        return None, None

def main():
    """
    Main function to read a text file, chunk it, and save the chunks to a json file.
    """
    parser = argparse.ArgumentParser(description="Ingest a text file, chunk it, and save to JSON")
    parser.add_argument("filename", help="The name of the text file in the 'data' directory.")
    args = parser.parse_args()

    input_filepath = args.filename
    base_name, _ = os.path.splitext(args.filename)
    output_filepath = os.path.join("data", f"{base_name}_chunks.json")


    text_context = read_file_content(input_filepath)
    if text_context:
        # Get AI=generated title and description
        doc_title, doc_description = get_ai_title_and_description(text_context)
        if not doc_title:
            doc_title = base_name
        safe_title = sanitize_filename(doc_title)
        output_filepath = os.path.join("data", f"{safe_title}_chunks.json")
        metadata_filepath = os.path.join("data", f"{safe_title}_metadata.json")
        chunks = chunk_text(text_context)
        print(f"Successfully chunked the file into {len(chunks)} chunks.")
        save_chunks_to_json(chunks, output_filepath)
        # Save description as metadata
        with open(metadata_filepath, "w", encoding="utf-8") as f:
            json.dump({"title": doc_title, "description": doc_description}, f, indent=4)
        print(f"Metadata saved to '{metadata_filepath}'")
    
if __name__ == "__main__":
    main()