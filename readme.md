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

To deepen my understanding of the project, I added several custom features and improvements. These include URL hashing using SHA-1 to ensure each website loads into a unique Chroma collection and avoid stale context, custom URL validation logic, proper session state resets when switching URLs, and clearer error handling. I also enhanced the interface flow to make it more intuitive and responsive, and customized the Streamlit theme. 