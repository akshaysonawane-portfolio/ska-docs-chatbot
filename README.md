SKA Documentation AI Chatbot
============================

An AI-powered chatbot that answers questions using **SKA developer documentation**.
The system crawls the documentation, converts it into embeddings, stores them in a vector database,
and retrieves relevant content to generate accurate answers.

The chatbot is built using a **Retrieval Augmented Generation (RAG)** architecture.


Features
--------

- Natural language search over SKA documentation
- Automatic documentation crawling
- Semantic search using embeddings
- Vector database for fast retrieval
- AI-generated answers with documentation context
- Chat interface built with Streamlit


Architecture
------------

The system follows a **Retrieval Augmented Generation (RAG)** pipeline.

::

   SKA Documentation Website
           ↓
        Crawler
           ↓
   Text Processing + Chunking
           ↓
        Embeddings
           ↓
   Vector Database (ChromaDB)
           ↓
      Similarity Search
           ↓
      LLM (GPT-4o-mini)
           ↓
      Generated Answer


How It Works
------------

1. Crawl Documentation
~~~~~~~~~~~~~~~~~~~~~~

The system crawls the SKA developer documentation website starting from::

   https://developer.skao.int/en/latest/

It recursively discovers internal documentation pages.

Example result::

   ~1600 documentation pages


2. Text Processing and Chunking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation pages are converted into plain text and split into smaller chunks.

Example::

   Chunk size ≈ 1000 characters

Result::

   1600 pages → ~30,000 text chunks

This improves retrieval accuracy.


3. Generate Embeddings
~~~~~~~~~~~~~~~~~~~~~~

Each chunk is converted into a vector representation using OpenAI embeddings.

Model used::

   text-embedding-3-small

These embeddings capture the semantic meaning of the text.


4. Store in Vector Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All embeddings are stored in **ChromaDB**, a vector database optimized for similarity search.

Each stored record contains::

   Embedding vector
   Text chunk
   Source URL


5. Similarity Search
~~~~~~~~~~~~~~~~~~~~

When a user asks a question::

   User Question → Embedding

The system retrieves the most relevant documentation chunks using vector similarity search.

Example::

   Top 10–12 relevant chunks


6. Generate Answer with LLM
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The retrieved documentation chunks are sent to an LLM.

Model used::

   GPT-4o-mini

The model generates a clear answer using the documentation context.


Project Structure
-----------------

::

   ska-docs-chatbot
   │
   ├── ingest.py        Documentation crawler and embedding pipeline
   ├── chatbot.py       Retrieval + LLM answer generation
   ├── app.py           Streamlit chatbot interface
   ├── requirements.txt
   ├── chroma_db/       Vector database (ignored in git)
   └── README.rst


Installation
------------

Clone the repository::

   git clone <repo-url>
   cd ska-docs-chatbot

Create virtual environment::

   python -m venv venv
   source venv/bin/activate

Install dependencies::

   pip install -r requirements.txt


Environment Setup
-----------------

Create a ``.env`` file and add your OpenAI API key::

   OPENAI_API_KEY=your_api_key_here


Build the Vector Database
-------------------------

Run the ingestion pipeline to crawl documentation and generate embeddings::

   python ingest.py

This will:

- crawl documentation pages
- split text into chunks
- generate embeddings
- store them in ChromaDB


Run the Chatbot
---------------

Start the Streamlit application::

   streamlit run app.py

Open the URL shown in the terminal.

Example questions::

   What is the SKA developer portal?
   How do I configure GitLab?
   What is containerisation in SKA?


Technologies Used
-----------------

Programming Language

- Python

Libraries

- Streamlit
- BeautifulSoup
- ChromaDB
- LangChain text splitters
- Requests

AI Models

- OpenAI Embeddings (text-embedding-3-small)
- GPT-4o-mini


Future Improvements
-------------------

Possible enhancements:

- Hybrid search (vector + keyword search)
- Incremental documentation updates
- Response streaming
- Slack or Teams integration
- Advanced reranking models


License
-------

This project is for educational and demonstration purposes.