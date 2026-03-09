import chromadb
from chromadb.config import Settings

chroma = chromadb.Client(Settings(persist_directory="./chroma_db"))

collection = chroma.get_collection("ska_docs")

print(collection.count())