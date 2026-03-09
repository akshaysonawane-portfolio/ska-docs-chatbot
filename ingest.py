import requests
from bs4 import BeautifulSoup
import chromadb
from openai import OpenAI
from uuid import uuid4

BASE_URL = "https://developer.skao.int/en/latest/"

client = OpenAI()

def get_links():

    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if href and href.startswith("http") and "developer.skao.int" in href:
            links.append(href)

    return list(set(links))


def extract_text(url):

    r = requests.get(url)

    soup = BeautifulSoup(r.text, "html.parser")

    return soup.get_text()


def chunk_text(text, size=800):

    chunks = []

    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])

    return chunks


def create_embeddings(text):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def main():

    links = get_links()

    chroma = chromadb.Client()

    collection = chroma.create_collection("ska_docs")

    for url in links:

        print("Processing:", url)

        text = extract_text(url)

        chunks = chunk_text(text)

        for chunk in chunks:

            embedding = create_embeddings(chunk)

            collection.add(
                ids=[str(uuid4())],
                embeddings=[embedding],
                documents=[chunk]
            )


if __name__ == "__main__":
    main()