import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_pdfs, load_txts, load_html, chunk_text
import os
import shutil

# Wipe and recreate the ChromaDB folder completely
if os.path.exists("chroma_db"):
    shutil.rmtree("chroma_db")

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Set up ChromaDB with persistent storage
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="bc_cs_docs")

def embed_and_store(all_chunks):
    """Embed all chunks and store in ChromaDB with metadata."""
    print(f"Embedding {len(all_chunks)} chunks...")
    
    texts = [chunk["text"] for chunk in all_chunks]
    ids = [chunk["chunk_id"] for chunk in all_chunks]
    metadatas = [{"source": chunk["source"]} for chunk in all_chunks]
    
    embeddings = model.encode(texts, show_progress_bar=True).tolist()
    
    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    print(f"Stored {len(all_chunks)} chunks in ChromaDB!")

def retrieve(query, k=5):
    """Retrieve top-k relevant chunks for a query."""
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    return results

if __name__ == "__main__":
    # Load and chunk all documents
    documents = load_pdfs() + load_txts() + load_html()
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"], doc["source"])
        all_chunks.extend(chunks)

    # Embed and store
    embed_and_store(all_chunks)

    # Test retrieval with 3 of your evaluation questions
    test_queries = [
    "What programming languages are CS undergrad students required to learn?",
    "What specialization does the CS department recommend for a graduate student that wishes to pursue a PhD?",
    "Are Professor Ziegler's exams pen and paper? Short answers or multiple choice? And are they allowed a cheat sheet?",
    "What negative feedback do students give about Professor Ziegler?",
    "If I take the expedited masters, does taking the graduate level computer theory course fulfill both undergrad and grad requirements at the same time?"
]
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        results = retrieve(query)
        for i, (doc, meta, distance) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            print(f"\nResult {i+1} (distance: {distance:.3f}) [{meta['source']}]")
            print(doc[:300])
