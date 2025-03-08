import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
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
LATEST_GEMINI_MODEL = "gemini-1.5-pro-latest"  # Always use the latest model

# Function to get the user's IP address
def get_user_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return response.json()["ip"]
    except:
        return "Unknown"

# Load banned IPs
def load_banned_ips():
    if os.path.exists(BANNED_IPS_FILE):
        with open(BANNED_IPS_FILE, "rb") as f:
            return pickle.load(f)
    return set()

# Save banned IPs
def save_banned_ips(banned_ips):
    with open(BANNED_IPS_FILE, "wb") as f:
        pickle.dump(banned_ips, f)

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

# Get user IP & check if banned
user_ip = get_user_ip()
banned_ips = load_banned_ips()

if user_ip in banned_ips:
    st.error("🚫 Your IP address has been banned due to suspicious activity.")
    st.stop()  # Block execution

# Load all chat sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chats()

# Sidebar - Chat Management
st.sidebar.header("📂 Chat Sessions")

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

# Ensure there's a selected chat
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
            st.rerun()  # Refresh UI

# Chat Delete Option
if st.session_state.current_chat:
    if st.sidebar.button("🗑️ Delete Chat"):
        del st.session_state.chat_sessions[st.session_state.current_chat]
        st.session_state.current_chat = chat_names[0] if chat_names else None
        save_chats()
        st.rerun()  # Refresh UI

# Ensure the selected chat session exists
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions[st.session_state.current_chat]
    messages = chat_data["messages"]
    timestamps = chat_data["timestamps"]
else:
    st.warning("Please create a new chat to start chatting!")
    st.stop()

# Initialize Chat Model with the latest Google Gemini model
chat_model = ChatGoogleGenerativeAI(model=LATEST_GEMINI_MODEL)

# Function to check if the question is related to Data Science
def is_data_science_question(question):
    keywords = ["data science", "machine learning", "AI", "deep learning", "statistics",
                "Python", "NumPy", "Pandas", "Matplotlib", "scikit-learn", "neural networks",
                "clustering", "regression", "classification", "time series", "data preprocessing"]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in keywords)

# Function to detect server exploitation attempts
def detect_exploit_attempts(question):
    exploit_keywords = ["hack", "bypass", "exploit", "DDoS", "SQL injection", "crash", "attack"]
    return any(keyword in question.lower() for keyword in exploit_keywords)

# User Input
user_input = st.chat_input("Ask me a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append User Message & Timestamp
    messages.insert(0, HumanMessage(content=user_input))
    timestamps.insert(0, timestamp)

    # Check for exploit attempts
    if detect_exploit_attempts(user_input):
        banned_ips.add(user_ip)
        save_banned_ips(banned_ips)
        st.error("🚨 Suspicious activity detected! Your IP has been banned.")
        st.stop()

    # Check if the question is related to Data Science
    if not is_data_science_question(user_input):
        response_text = "I'm here to assist with Data Science topics only. Please ask a Data Science-related question."
    else:
        # Retrieve Chat History
        chat_history = [msg for msg in messages if isinstance(msg, AIMessage)]
        
        # Generate AI Response
        response = chat_model.predict_messages(chat_history + [HumanMessage(content=user_input)])
        response_text = response.content

    # Append AI Response & Timestamp
    response_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.insert(1, AIMessage(content=response_text))
    timestamps.insert(1, response_timestamp)

    # Save chat session
    save_chats()

# Display Chat History (User Messages First)
for msg, timestamp in zip(messages, timestamps):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
