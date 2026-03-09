import chromadb
from openai import OpenAI

client = OpenAI()

chroma = chromadb.Client()

collection = chroma.get_collection("ska_docs")


def ask(question):

    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    results = collection.query(
        query_embeddings=[embedding],
        n_results=3
    )

    context = "\n".join(results["documents"][0])

    prompt = f"""
    Use this documentation context to answer the question.

    {context}

    Question: {question}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    return response.choices[0].message.content