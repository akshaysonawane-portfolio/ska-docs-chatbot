import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from uuid import uuid4
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

# -----------------------------
# Load API key
# -----------------------------

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_URL = "https://developer.skao.int/en/latest/"
MAX_PAGES = 1500
BATCH_SIZE = 100

# -----------------------------
# Text splitter
# -----------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# -----------------------------
# Crawl documentation
# -----------------------------

def crawl_docs():

    print("Starting recursive crawl...")

    visited = set()
    queue = [BASE_URL]
    docs = []

    while queue and len(docs) < MAX_PAGES:

        url = queue.pop(0)

        if url in visited:
            continue

        visited.add(url)

        print("Scanning:", url)

        try:
            r = requests.get(url, timeout=10)
        except:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        docs.append(url)

        for link in soup.find_all("a"):

            href = link.get("href")

            if not href:
                continue

            full_url = urljoin(url, href)

            if "developer.skao.int" not in full_url:
                continue

            if "#" in full_url:
                continue

            if full_url.endswith((".png",".jpg",".svg",".css",".js",".pdf")):
                continue

            if full_url not in visited and full_url not in queue:
                queue.append(full_url)

        print("Pages discovered:", len(docs))

        time.sleep(0.1)

    print("Total documentation pages discovered:", len(docs))

    return docs


# -----------------------------
# Extract page text
# -----------------------------

def extract_text(url):

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(separator="\n")
    except:
        print("Failed:", url)
        return ""


# -----------------------------
# Batch embedding
# -----------------------------

def create_embeddings_batch(texts):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    return [d.embedding for d in response.data]


# -----------------------------
# Main ingestion
# -----------------------------

def main():

    print("Starting full SKA documentation ingestion...")

    urls = crawl_docs()

    chroma = chromadb.Client(
        Settings(
            persist_directory="./chroma_db",
            is_persistent=True
        )
    )

    collection = chroma.get_or_create_collection("ska_docs")

    all_chunks = []
    all_metadata = []

    for url in urls:

        print("Processing:", url)

        text = extract_text(url)

        if not text:
            continue

        chunks = splitter.split_text(text)

        for chunk in chunks:

            if len(chunk.strip()) < 100:
                continue

            all_chunks.append(chunk)
            all_metadata.append({"source": url})

    print("Total chunks:", len(all_chunks))

    # -----------------------------
    # Batch embeddings
    # -----------------------------

    for i in range(0, len(all_chunks), BATCH_SIZE):

        batch = all_chunks[i:i+BATCH_SIZE]
        meta = all_metadata[i:i+BATCH_SIZE]

        print("Embedding batch", i, "-", i+len(batch))

        embeddings = create_embeddings_batch(batch)

        collection.add(
            ids=[str(uuid4()) for _ in batch],
            embeddings=embeddings,
            documents=batch,
            metadatas=meta
        )

    print("Ingestion complete")


if __name__ == "__main__":
    main()