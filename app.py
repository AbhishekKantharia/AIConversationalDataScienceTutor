import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage
import google.generativeai as genai
import datetime
import os
import pickle
import requests
from dotenv import load_dotenv  # Secure password storage

# Load environment variables securely
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# File Paths
CHAT_SESSIONS_FILE = "chat_sessions.pkl"
BANNED_IPS_FILE = "banned_ips.pkl"
LATEST_GEMINI_MODEL = "gemini-1.5-pro-latest"

# Streamlit Page Config (Dark Mode Only)
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

# Apply Full Dark Mode Theme
st.markdown(
    """
    <style>
        body { background-color: #121212; color: #e0e0e0; }
        .stApp { background-color: #121212; }
        .stButton>button { background-color: #333; color: white; border-radius: 10px; }
        .stTextInput>div>div>input { background-color: #222; color: white; border: 1px solid #555; }
        .stSidebar { background-color: #181818; }
        .stSidebar .stButton>button { background-color: #333; color: white; }
        .stSidebar .stTextInput>div>div>input { background-color: #222; color: white; border: 1px solid #555; }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to get the user's IP address
def get_user_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return response.json()["ip"]
    except:
        return "Unknown"

# Load & Save Banned IPs
def load_banned_ips():
    return pickle.load(open(BANNED_IPS_FILE, "rb")) if os.path.exists(BANNED_IPS_FILE) else set()

def save_banned_ips(banned_ips):
    pickle.dump(banned_ips, open(BANNED_IPS_FILE, "wb"))

# Load & Save Chat Sessions
def load_chats():
    return pickle.load(open(CHAT_SESSIONS_FILE, "rb")) if os.path.exists(CHAT_SESSIONS_FILE) else {}

def save_chats():
    pickle.dump(st.session_state.chat_sessions, open(CHAT_SESSIONS_FILE, "wb"))

# Get user IP & check if banned
user_ip = get_user_ip()
banned_ips = load_banned_ips()

if user_ip in banned_ips:
    st.error("🚫 Your IP address has been banned due to suspicious activity.")
    st.stop()

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
    st.session_state.current_chat = chat_names[0] if chat_names else None

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

# Admin-Only Feature: Unblock IP Addresses
st.sidebar.header("🔓 Unblock IPs (Admin Only)")
admin_password = st.sidebar.text_input("Enter Admin Password:", type="password")

if admin_password and admin_password == ADMIN_PASSWORD:
    unblock_ip = st.sidebar.text_input("Enter IP to Unblock:")
    if st.sidebar.button("✅ Unblock IP"):
        if unblock_ip in banned_ips:
            banned_ips.remove(unblock_ip)
            save_banned_ips(banned_ips)
            st.sidebar.success(f"✅ IP {unblock_ip} has been unblocked.")
        else:
            st.sidebar.warning(f"⚠️ IP {unblock_ip} is not banned.")

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

# User Input
user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.insert(0, HumanMessage(content=user_input))
    timestamps.insert(0, timestamp)

    chat_history = [msg for msg in messages if isinstance(msg, AIMessage)]
    response = chat_model.invoke(chat_history + [HumanMessage(content=user_input)])
    response_text = response.content

    messages.insert(1, AIMessage(content=response_text))
    timestamps.insert(1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    save_chats()

# Display Chat Messages
for msg, timestamp in zip(messages, timestamps):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
