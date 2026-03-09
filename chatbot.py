import chromadb
from chromadb.config import Settings
import os
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------
# Load API key
# -----------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# -----------------------------
# Connect to ChromaDB
# -----------------------------

chroma = chromadb.Client(
    Settings(
        persist_directory="./chroma_db",
        is_persistent=True
    )
)

collection = chroma.get_collection("ska_docs")


# -----------------------------
# Ask Question
# -----------------------------

def ask(question):

    # Create embedding for query
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    # Retrieve similar documents
    results = collection.query(
        query_embeddings=[embedding],
        n_results=12
    )

    docs = results.get("documents", [])
    sources = results.get("metadatas", [])

    print("Documents retrieved:", len(docs[0]) if docs else 0)

    if not docs or len(docs[0]) == 0:
        return "No relevant documentation found."

    # Combine retrieved chunks
    context = "\n\n".join(docs[0])

    prompt = f"""
You are an assistant that answers questions using SKA developer documentation.

Answer using ONLY the documentation context below.

If the context only partially answers the question,
provide the closest relevant explanation from the documentation.

Do NOT invent information.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    # Collect source links
    source_links = []

    if sources and len(sources[0]) > 0:
        for m in sources[0]:
            if "source" in m:
                source_links.append(m["source"])

    if source_links:
        answer += "\n\nSources:\n" + "\n".join(set(source_links))

    return answer