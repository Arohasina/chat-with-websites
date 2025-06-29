import streamlit as st 
import requests
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


load_dotenv() #load the .env file

def get_vectorstore_from_url(url):
    #to get the text in document format from the website
    loader = WebBaseLoader(url)
    documents = loader.load()

    #to split the text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(documents)

    #create a vectorstore from the document chunks
    vector_store = Chroma.from_documents(document_chunks, OpenAIEmbeddings())
    
    return vector_store

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI()
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"), 
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. ")
    ])

    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    llm = ChatOpenAI()

    prompt= ChatPromptTemplate.from_messages([
        ("system", "Answer the user's question based on the below context:\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
    ])

    stuff_document_chain= create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_document_chain) 

def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    converstation_rag_chain = get_conversational_rag_chain(retriever_chain)

    response = converstation_rag_chain.invoke({
            "chat_history": st.session_state.chat_history,
            "input": user_input
        })
    
    return response['answer']

#app configuration
st.set_page_config(page_title="Chat with Website",page_icon= "💬")
st.title("Chat with Website")

# Sidebar
with st.sidebar:
    st.header("Settings")
    website_url = st.text_input(
        "Website URL",
        placeholder="Please paste the website URL here...",
        help="Enter the full URL (e.g., https://example.com)")

#Session State Setup:
# Initialize last_url to remember previously loaded URL
if "last_url" not in st.session_state:
    st.session_state.last_url = ""
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


#URL Validation & Loading:
# Check if a new, well-formed, accessible URL was entered
if website_url is None or website_url.strip() == "":
    st.info("Please enter a valid website URL to start chatting.")
elif not website_url.startswith("http"):
    st.warning("Please make sure your URL starts with http:// or https://")
elif website_url != st.session_state.last_url:
    try:
        response = requests.head(website_url, allow_redirects=True, timeout=5)
        if response.status_code >= 400:
            st.error(f"Website returned an error (status code {response.status_code}). Please check the URL.")
            st.session_state.vector_store = None
        else:
            st.session_state.vector_store = get_vectorstore_from_url(website_url)
            st.session_state.last_url = website_url
            st.session_state.chat_history = [
                AIMessage(content="Website loaded! You can start asking questions.")
            ]
    except requests.RequestException as e:
        st.error(f"Failed to access the website. Error: {e}")
        st.session_state.vector_store = None


#Chat Interface:
if st.session_state.vector_store:
    user_query = st.chat_input("Type your message here...")
    if user_query:
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
else:
    st.info("Chat input will appear once a valid website is loaded.")
    






