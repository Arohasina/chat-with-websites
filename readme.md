# Chat with Website

This is a Streamlit web app that lets you chat with the content of any public website URL.  
It uses LangChain with OpenAI embeddings and Chat models to:  
- Load and scrape the website text  
- Split the text into chunks and embed them into a vector store (Chroma)  
- Run a conversational retrieval-augmented generation (RAG) chat over the website content  

## Features

- Enter any URL to load its text content  
- Ask questions about the website content in a chat interface  
- Context-aware conversation with chat history  

## Credit
This project was built as a learning exercise by following the tutorial from [alejandro-ao/chat-with-websites](https://youtu.be/bupx08ZgSFg?si=zxUf1Gf3QHxJfAHY). I wanted to practice working with LangChain, Streamlit, and retrieval-augmented generation (RAG) while gaining hands-on experience building a real-world chatbot application.

The tutorial covered key concepts like:

Using LangChain with large language models (e.g. GPT-4)

Building a Streamlit interface for dynamic website interaction

Implementing vector stores (ChromaDB) and conversational RAG pipelines

To deepen my understanding, I added my own twists to the project, including custom URL validation logic, better interface flow, and improvements in session handling and error feedback.