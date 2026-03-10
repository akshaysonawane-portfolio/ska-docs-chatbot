import chromadb
from chromadb.config import Settings
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# -----------------------
# Connect DB
# -----------------------

chroma = chromadb.Client(
    Settings(
        persist_directory="./chroma_db",
        is_persistent=True
    )
)

collection = chroma.get_collection("ska_docs")


# -----------------------
# Ask question
# -----------------------

def ask(question):

    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    results = collection.query(
        query_embeddings=[embedding],
        n_results=14
    )

    docs = results.get("documents", [])
    sources = results.get("metadatas", [])

    print("Documents retrieved:", len(docs[0]) if docs else 0)

    if not docs or len(docs[0]) == 0:
        return "No relevant documentation found."

    context = "\n\n".join(docs[0])

    prompt = f"""
You are an expert assistant for SKA developer documentation.

Answer the question using ONLY the context below.

If the context partially answers the question,
provide the closest relevant explanation.

Do NOT invent information.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    # Add sources
    source_links = []

    if sources and len(sources[0]) > 0:
        for m in sources[0]:
            if "source" in m:
                source_links.append(m["source"])

    # if source_links:
    #     answer += "\n\n📚 Sources:\n"
    #     for link in set(source_links):
    #         answer += f"- {link}\n"

    return answer