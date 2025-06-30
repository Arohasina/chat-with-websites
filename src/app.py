import streamlit as st 
import requests
import os
from langchain.schema import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from hashlib import sha1
from pinecone import Pinecone

load_dotenv() #load the .env file

# Initialize Pinecone
def init_pinecone():
    # Try to get API key from environment variables or Streamlit secrets
    try:
        api_key = os.getenv("PINECONE_API_KEY") or st.secrets.get("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME") or st.secrets.get("PINECONE_INDEX_NAME", "chatwithwebsite-index")
    except:
        # Fallback to environment variables only
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME", "chatwithwebsite-index")
    
    if not api_key:
        raise ValueError("Pinecone API key not found. Please check your environment variables or Streamlit secrets.")
    
    pc = Pinecone(api_key=api_key)
    return pc, index_name

def get_vectorstore_from_url(url):
    #to get the text in document format from the website
    loader = WebBaseLoader(url)
    documents = loader.load()

    #to split the text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(documents)

    # Initialize Pinecone
    pc, index_name = init_pinecone()
    
    # Create a unique namespace for this URL to avoid conflicts
    url_hash = sha1(url.encode()).hexdigest()
    namespace = f"website-{url_hash}"
    
    # Create embeddings - handle API key for Streamlit Cloud
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    except:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    
    # Create vectorstore from documents using Pinecone
    vector_store = PineconeVectorStore.from_documents(
        documents=document_chunks,
        embedding=embeddings,
        index_name=index_name,
        namespace=namespace
    )
    
    return vector_store, namespace

def get_context_retriever_chain(vector_store):
    # Handle OpenAI API key for Streamlit Cloud
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    except:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    
    llm = ChatOpenAI(api_key=openai_api_key)
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"), 
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. ")
    ])

    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    # Handle OpenAI API key for Streamlit Cloud
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    except:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    
    llm = ChatOpenAI(api_key=openai_api_key)

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

def clear_previous_vectors():
    """Clear vectors from previous URL if exists"""
    if hasattr(st.session_state, 'current_namespace') and st.session_state.current_namespace:
        try:
            pc, index_name = init_pinecone()
            index = pc.Index(index_name)
            # Delete all vectors in the namespace
            index.delete(delete_all=True, namespace=st.session_state.current_namespace)
        except Exception as e:
            st.warning(f"Could not clear previous vectors: {e}")

#app configuration
st.set_page_config(page_title="Chat with Website",page_icon= "💬")
st.title("Chat with any Website🌐")

with st.sidebar:
    st.header("Settings")
    website_url = st.text_input(
        "Website URL",
        placeholder="Please paste the website URL here...",
        help="Enter the full URL (e.g., https://example.com)")
    
    # Add a button to load the website
    load_button = st.button("Load Website", type="primary")
    
    # Add clear button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        if hasattr(st.session_state, 'current_namespace'):
            clear_previous_vectors()
        st.rerun()

#Session State Setup:
# Initialize session state variables if not already present
if "last_url" not in st.session_state:
    st.session_state.last_url = ""
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_namespace" not in st.session_state:
    st.session_state.current_namespace = None

#URL Validation & Loading:
# Check if a new, well-formed, accessible URL was entered
if website_url is None or website_url.strip() == "":
    st.info("Please enter a valid website URL to start chatting.")

elif not website_url.startswith("http"):
    st.warning("Please make sure your URL starts with http:// or https://")

elif (load_button or website_url != st.session_state.last_url) and website_url.strip() != "":
    try:
        response = requests.head(website_url, allow_redirects=True, timeout=5)
        if response.status_code >= 400:
            st.error(f"Website returned an error (status code {response.status_code}). Please check the URL.")
            st.session_state.vector_store = None
        else:
            # Clear previous vectors if changing URLs
            if st.session_state.last_url != "":
                clear_previous_vectors()
            
            with st.spinner("Loading website content... This may take a moment."):
                st.session_state.vector_store, namespace = get_vectorstore_from_url(website_url)
                st.session_state.current_namespace = namespace
                st.session_state.chat_history = [AIMessage(content="Website loaded! You can start asking questions.")]
                st.session_state.last_url = website_url
    except requests.RequestException as e:
        st.error(f"Failed to access the website. Error: {e}")
        st.session_state.vector_store = None
    except Exception as e:
        st.error(f"Failed to process the website. Error: {e}")
        st.session_state.vector_store = None

#Chat Interface - only shows if vector store is loaded:
if st.session_state.vector_store:
    user_query = st.chat_input("Type your message here...")
    if user_query:
        try:
            response = get_response(user_query)
            st.session_state.chat_history.append(HumanMessage(content=user_query))
            st.session_state.chat_history.append(AIMessage(content=response))
        except Exception as e:
            st.error(f"Error processing your question: {e}")

    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)

else:
    st.info("Chat input will appear once a valid website is loaded.")