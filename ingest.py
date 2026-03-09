import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from uuid import uuid4
import os
from dotenv import load_dotenv

# -----------------------------
# Load API key
# -----------------------------

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

BASE_URL = "https://developer.skao.int/en/latest/"

# -----------------------------
# Collect documentation links
# -----------------------------

def get_links():

    print("Collecting links...")

    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []

    for link in soup.find_all("a"):

        href = link.get("href")

        if not href:
            continue

        full_url = urljoin(BASE_URL, href)

        if "developer.skao.int" not in full_url:
            continue

        if "#" in full_url:
            continue

        links.append(full_url)

    links = list(set(links))

    print("Total links found:", len(links))

    return links


# -----------------------------
# Extract page text
# -----------------------------

def extract_text(url):

    try:

        r = requests.get(url, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text(separator="\n")

        return text

    except Exception as e:

        print("Failed:", url)

        return ""


# -----------------------------
# Split document into chunks
# -----------------------------

def chunk_text(text, size=800):

    chunks = []

    for i in range(0, len(text), size):

        chunk = text[i:i+size]

        chunks.append(chunk)

    return chunks


# -----------------------------
# Create embeddings
# -----------------------------

def create_embedding(text):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


# -----------------------------
# Main ingestion pipeline
# -----------------------------

def main():

    print("Starting ingestion...")

    links = get_links()

    chroma = chromadb.Client(
        Settings(
            persist_directory="./chroma_db",
            is_persistent=True
        )
    )

    collection = chroma.get_or_create_collection("ska_docs")

    for url in links:

        print("Processing:", url)

        text = extract_text(url)

        if not text:
            continue

        chunks = chunk_text(text)

        for chunk in chunks:

            try:

                embedding = create_embedding(chunk)

                collection.add(
                    ids=[str(uuid4())],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": url}]
                )

            except Exception:

                print("Embedding failed")
    print("Total stored docs:", collection.count())
    print("Ingestion complete")


if __name__ == "__main__":
    main()