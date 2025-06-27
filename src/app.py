import streamlit as st 
from langchain_core.messages import AIMessage, HumanMessage

def get_response(user_input):
    return "I don't know"

#app configuration
st.set_page_config(page_title="Chat with Website",page_icon= "💬")
st.title("Chat with Website")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! How can I help you?"),
    ]


# Sidebar
with st.sidebar:
    st.header("Settings")
    website_url = st.text_input(
        "Website URL",
        placeholder="Please paste the website URL here...",
        help="Enter the full URL (e.g., https://example.com)")
    
if website_url is None or website_url == "":
    st.info("Please enter a valid website URL to start chatting.")

else:
    #user input
    user_query = st.chat_input("Type your message here...",)
    if user_query is not None and user_query != "":
        response= get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

    #conversation 
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("Human"):
                st.write(message.content)







