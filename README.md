# SKA Documentation Chatbot

This project builds an AI chatbot that answers questions using
SKA developer documentation.

Docs source:
https://developer.skao.int/en/latest/

## Features

- Crawls SKA documentation
- Converts pages into embeddings
- Stores them in a vector database
- Uses GPT to answer questions

## Setup

pip install -r requirements.txt

## Build Knowledge Base

python ingest.py

## Run Chatbot

streamlit run app.py