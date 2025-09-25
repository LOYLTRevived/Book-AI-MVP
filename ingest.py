#ingest.py

import os
import json
import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz #PyMuPDF
from ebooklib import epub
from bs4 import BeautifulSoup 



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
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
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

def main():
    """
    Main function to read a text file, chunk it, and save the chunks to a json file.
    """
    parser = argparse.ArgumentParser(description="Ingest a text file, chunk it, and save to JSON")
    parser.add_argument("filename", help="The name of the text file in the 'data' directory.")
    args = parser.parse_args()

    input_filepath = os.path.join("data", args.filename)
    base_name, _ = os.path.splitext(args.filename)
    output_filepath = os.path.join("data", f"{base_name}_chunks.json")

    text_context = read_text_file(input_filepath)
    if text_context:
        chunks = chunk_text(text_context)
        print(f"successfully chunked the file into {len(chunks)} chunks.")
        save_chunks_to_json(chunks, output_filepath)
    
if __name__ == "__main__":
    main()