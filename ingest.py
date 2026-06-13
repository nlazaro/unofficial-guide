import pdfplumber
import os
import re

def clean_text(text, source):
    """Clean noise from text based on source type."""
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}', '', text)
    
    if source.endswith('.pdf'):
        # Remove page numbers (standalone numbers)
        text = re.sub(r'\n\d+\n', ' ', text)
        # Remove table of contents dots
        text = re.sub(r'\.{3,}', ' ', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

DOCS_PATH = "ai201-project1-unofficial-guide-starter/documents"
CHUNK_SIZE = 200  # tokens, approximated as words
OVERLAP = 30

def load_pdfs():
    """Load all PDFs from the docs folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".pdf"):
            filepath = os.path.join(DOCS_PATH, filename)
            with pdfplumber.open(filepath) as pdf:
                text = "\n\n".join(
                    page.extract_text() for page in pdf.pages 
                    if page.extract_text()
                )
            text = clean_text(text, filename)
            documents.append({
                "source": filename,
                "text": text
            })
            print(f"Loaded: {filename} ({len(text)} characters)")
    return documents

def load_txts():
    """Load all .txt files from the docs folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            text = clean_text(text, filename)
            documents.append({
                "source": filename,
                "text": text
            })
            print(f"Loaded: {filename} ({len(text)} characters)")
    return documents

import re

def load_html():
    """Load and clean HTML files from the docs folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".html"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
            # Strip HTML tags
            text = re.sub(r'<[^>]+>', ' ', raw)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            text = clean_text(text, filename)
            documents.append({
                "source": filename,
                "text": text
            })
            print(f"Loaded: {filename} ({len(text)} characters)")
    return documents

def chunk_text(text, source):
    """Split text into chunks with overlap."""
    words = text.split()
    chunks = []
    counter = 0
    start = 0

    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_words) >= 20:
            chunks.append({
                "text": chunk_text,
                "source": source,
                "chunk_id": f"{source}_{counter}"
            })
            counter += 1

        start += CHUNK_SIZE - OVERLAP

    return chunks

if __name__ == "__main__":
    documents = load_pdfs() + load_txts() + load_html()
    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc["text"], doc["source"])
        all_chunks.extend(chunks)
        print(f"{doc['source']}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    discord_chunks = [c for c in all_chunks if 'discord' in c['source']]
    for chunk in discord_chunks[:3]:
        print(f"\n[{chunk['chunk_id']}]\n{chunk['text']}\n")