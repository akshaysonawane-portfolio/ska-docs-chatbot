import streamlit as st
from chatbot import ask

st.title("SKA Documentation Chatbot")

question = st.text_input("Ask about SKA documentation")

if question:

    answer = ask(question)

    st.write(answer)