# Chat with Any Website 🌐💬

This project was built as a learning exercise by following the tutorial from [alejandro-ao/chat-with-websites](https://github.com/alejandro-ao/chat-with-websites). To practice working with LangChain, Streamlit, and retrieval-augmented generation (RAG) while experiencing building a real-world chatbot application.

## Live Demo

Try the application here: **https://chat-with-websites-bq7pkc847ate3fns3uzul4.streamlit.app/**

## Custom Features & Improvements

To deepen my understanding of the project, I added several custom features and improvements to the original tutorial:

### Core Enhancements
- **Migrated from Chroma to Pinecone** Deployment fails on Streamlit Cloud due to Chroma's SQLite version requirement. Chroma requires sqlite3 >= 3.35.0, but Streamlit Cloud runs an older version causing compatibility issues. Switching to Pinecone eliminates SQLite dependencies and ensures cloud deployment compatibility.
- **URL hashing using SHA-1** to ensure each website loads into a unique namespace and avoid stale context
- **Custom URL validation logic** with helpful error messages and next steps
- **Proper session state management** with automatic resets when switching URLs
- **Enhanced error handling** with actionable troubleshooting steps

### User Experience
- **Load Website button** for explicit control over when to process URLs
- **Improved interface flow** with clear visual feedback and loading states
- **Clean chat history functionality** with vector cleanup
- **Customized Streamlit theme** for a more polished appearance

## Features

- **Chat with any website** - Load content from any public URL
- **Persistent conversations** - Maintains chat history during your session
- **Context-aware responses** - Uses RAG to provide accurate answers based on website content
- **URL isolation** - Each website gets its own namespace to prevent data mixing
- **Smart error handling** - Clear feedback when websites can't be accessed or processed

## Technologies Used

- **LangChain** - Framework for building LLM applications
- **Streamlit** - Web app framework for the user interface
- **Pinecone** - Vector database for persistent storage
- **OpenAI** - Language model and embeddings
- **Python** - Core programming language