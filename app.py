import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage
import google.generativeai as genai
import datetime
import os
import pickle
import requests
import bcrypt
import streamlit_authenticator as stauth
from dotenv import load_dotenv

# Load environment variables securely
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
USER_PASSWORD = os.getenv("USER_PASSWORD")

# Hardcoded usernames & roles (can be extended with a database)
CREDENTIALS = {
    "admin": {"password": ADMIN_PASSWORD, "role": "admin"},
    "user": {"password": USER_PASSWORD, "role": "user"}
}

# Hash passwords securely
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify password
def verify_password(stored_password, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_password.encode())

# Function to authenticate user
def authenticate(username, password):
    if username in CREDENTIALS and verify_password(CREDENTIALS[username]["password"], password):
        return CREDENTIALS[username]["role"]
    return None

# Streamlit UI Setup
st.set_page_config(page_title="ChatGPT Clone - Free AI Data Science Tutor", layout="wide")

# Login UI
st.sidebar.header("🔑 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

# Check authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None

if login_button:
    role = authenticate(username, password)
    if role:
        st.session_state.authenticated = True
        st.session_state.user_role = role
        st.sidebar.success(f"✅ Logged in as {username} ({role.capitalize()})")
        st.experimental_rerun()
    else:
        st.sidebar.error("❌ Invalid credentials!")

# Block unauthorized users
if not st.session_state.authenticated:
    st.stop()

# File Paths
CHAT_SESSIONS_FILE = "chat_sessions.pkl"
BANNED_IPS_FILE = "banned_ips.pkl"
LATEST_GEMINI_MODEL = "gemini-1.5-pro-latest"

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

# Admin-Only Feature: Unblock IP Addresses
if st.session_state.user_role == "admin":
    st.sidebar.header("🔓 Unblock IPs (Admin Only)")
    unblock_ip = st.sidebar.text_input("Enter IP to Unblock:")
    if st.sidebar.button("✅ Unblock IP"):
        banned_ips = load_banned_ips()
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
user_input = st.chat_input("Ask me a Data Science question...")

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

for msg, timestamp in zip(messages, timestamps):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
