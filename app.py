import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage
import google.generativeai as genai
import datetime
import os
import pickle
import requests

# Set API Key
genai.configure(api_key="your_actual_api_key_here")

# File Paths
CHAT_SESSIONS_FILE = "chat_sessions.pkl"
BANNED_IPS_FILE = "banned_ips.pkl"
LATEST_GEMINI_MODEL = "gemini-1.5-pro-latest"

# Streamlit UI Setup
st.set_page_config(page_title="ChatGPT Clone - AI Data Science Tutor", layout="wide")

# Load chat sessions
def load_chats():
    if os.path.exists(CHAT_SESSIONS_FILE):
        with open(CHAT_SESSIONS_FILE, "rb") as f:
            return pickle.load(f)
    return {}

# Save chat sessions
def save_chats():
    with open(CHAT_SESSIONS_FILE, "wb") as f:
        pickle.dump(st.session_state.chat_sessions, f)

# Load all chat sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chats()

# Sidebar - ChatGPT-Style Layout
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg", width=60)
st.sidebar.title("ChatGPT Clone")
st.sidebar.markdown("**AI Data Science Tutor** - Powered by Google Gemini")

# Create a new chat
if st.sidebar.button("➕ New Chat"):
    new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions[new_chat_id] = {"messages": [], "timestamps": []}
    st.session_state.current_chat = new_chat_id
    save_chats()

# Select existing chat
chat_names = list(st.session_state.chat_sessions.keys())
if chat_names:
    selected_chat = st.sidebar.radio("💬 Select a Chat", chat_names)
    st.session_state.current_chat = selected_chat

# Ensure a chat is selected
if "current_chat" not in st.session_state or st.session_state.current_chat not in st.session_state.chat_sessions:
    if chat_names:
        st.session_state.current_chat = chat_names[0]
    else:
        st.session_state.current_chat = None

# Chat Rename Option
if st.session_state.current_chat:
    new_chat_name = st.sidebar.text_input("✏️ Rename Chat", value=st.session_state.current_chat)
    if st.sidebar.button("✅ Save Name"):
        if new_chat_name and new_chat_name not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[new_chat_name] = st.session_state.chat_sessions.pop(st.session_state.current_chat)
            st.session_state.current_chat = new_chat_name
            save_chats()
            st.rerun()

# Chat Delete Option
if st.session_state.current_chat:
    if st.sidebar.button("🗑️ Delete Chat"):
        del st.session_state.chat_sessions[st.session_state.current_chat]
        st.session_state.current_chat = chat_names[0] if chat_names else None
        save_chats()
        st.rerun()

# Ensure chat session exists
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions[st.session_state.current_chat]
    messages = chat_data["messages"]
    timestamps = chat_data["timestamps"]
else:
    st.warning("Please create a new chat to start chatting!")
    st.stop()

# Initialize Chat Model with the latest Google Gemini model
chat_model = ChatGoogleGenerativeAI(model=LATEST_GEMINI_MODEL)

# Function to check if question is Data Science-related
def is_data_science_question(question):
    keywords = ["data science", "machine learning", "AI", "deep learning", "statistics",
                "Python", "NumPy", "Pandas", "Matplotlib", "scikit-learn", "neural networks",
                "clustering", "regression", "classification", "time series", "data preprocessing"]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in keywords)

# Chat Message Container
st.title("🤖 ChatGPT Clone - AI Data Science Tutor")

chat_container = st.container()

# Display Chat History (Mimicking ChatGPT UI)
with chat_container:
    for msg, timestamp in zip(messages, timestamps):
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(f"**[{timestamp}]** {msg.content}")

# User Input
user_input = st.chat_input("Ask me a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    messages.insert(0, HumanMessage(content=user_input))
    timestamps.insert(0, timestamp)

    if not is_data_science_question(user_input):
        response_text = "I'm here to assist with Data Science topics only."
    else:
        chat_history = [msg for msg in messages if isinstance(msg, AIMessage)]
        response = chat_model.invoke(chat_history + [HumanMessage(content=user_input)])

        # Streaming Response Like ChatGPT
        response_text = ""
        with st.chat_message("assistant"):
            for chunk in response.content.split():
                response_text += chunk + " "
                st.markdown(response_text)

    messages.insert(1, AIMessage(content=response_text))
    timestamps.insert(1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    save_chats()
