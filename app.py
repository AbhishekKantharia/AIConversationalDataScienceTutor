import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage
import google.generativeai as genai
import datetime
import os
import pickle
import requests
from dotenv import load_dotenv  # Secure password storage
from fpdf import FPDF  # PDF Export

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

# Streamlit Page Config
st.set_page_config(page_icon="🤖", layout="wide")

# Streamlit Project Title
st.title("AI Data Science Tutor 🤖")

# Sidebar - Feature Toggles
st.sidebar.header("⚙️ Toggle Features")
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "multi_chat" not in st.session_state:
    st.session_state.multi_chat = True
if "pdf_export" not in st.session_state:
    st.session_state.pdf_export = True
if "chat_summarization" not in st.session_state:
    st.session_state.chat_summarization = True
if "ip_banning" not in st.session_state:
    st.session_state.ip_banning = True

# Toggle buttons
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.multi_chat = st.sidebar.toggle("💬 Enable Multi-Chat", value=st.session_state.multi_chat)
st.session_state.pdf_export = st.sidebar.toggle("📜 Enable PDF Export", value=st.session_state.pdf_export)
st.session_state.chat_summarization = st.sidebar.toggle("🧠 Enable AI Summarization", value=st.session_state.chat_summarization)
st.session_state.ip_banning = st.sidebar.toggle("🔐 Enable IP Banning", value=st.session_state.ip_banning)

# Apply Dark/Light Mode Styling
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        body { background-color: #121212; color: #e0e0e0; }
        .stApp { background-color: #121212; }
        .stButton>button { background: linear-gradient(145deg, #1f1f1f, #292929); color: white; border-radius: 10px; }
        .stChatMessage { background: linear-gradient(145deg, #1e1e1e, #252525); padding: 12px; border-radius: 10px; }
        .stTextInput>div>div>input { background: #222; color: white; border: 1px solid #555; }
        .stSidebar { background-color: #181818; }
        </style>
        """,
        unsafe_allow_html=True
    )

# Load Chat Sessions & Banned IPs
def load_banned_ips():
    return pickle.load(open(BANNED_IPS_FILE, "rb")) if os.path.exists(BANNED_IPS_FILE) else set()

def save_banned_ips(banned_ips):
    pickle.dump(banned_ips, open(BANNED_IPS_FILE, "wb"))

def load_chats():
    return pickle.load(open(CHAT_SESSIONS_FILE, "rb")) if os.path.exists(CHAT_SESSIONS_FILE) else {}

def save_chats():
    pickle.dump(st.session_state.chat_sessions, open(CHAT_SESSIONS_FILE, "wb"))

# IP Banning (if enabled)
if st.session_state.ip_banning:
    def get_user_ip():
        try:
            response = requests.get("https://api64.ipify.org?format=json")
            return response.json()["ip"]
        except:
            return "Unknown"

    user_ip = get_user_ip()
    banned_ips = load_banned_ips()
    if user_ip in banned_ips:
        st.error("🚫 Your IP has been banned.")
        st.stop()

# Multi-Chat Support (if enabled)
if st.session_state.multi_chat:
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = load_chats()

    st.sidebar.header("📂 Chat Sessions")

    if st.sidebar.button("➕ New Chat"):
        new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_chat_id] = {"messages": [], "timestamps": []}
        st.session_state.current_chat = new_chat_id
        save_chats()

    chat_names = list(st.session_state.chat_sessions.keys())
    if chat_names:
        selected_chat = st.sidebar.radio("💬 Select a Chat", chat_names)
        st.session_state.current_chat = selected_chat

    if "current_chat" not in st.session_state or st.session_state.current_chat not in st.session_state.chat_sessions:
        st.session_state.current_chat = chat_names[0] if chat_names else None

    # Delete Chat Option
    if st.session_state.current_chat:
        if st.sidebar.button("🗑️ Delete Chat"):
            del st.session_state.chat_sessions[st.session_state.current_chat]
            chat_names = list(st.session_state.chat_sessions.keys())  
            st.session_state.current_chat = chat_names[0] if chat_names else None
            save_chats()
            st.experimental_rerun()

# Ensure chat_data is properly initialized
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions[st.session_state.current_chat]
else:
    chat_data = {"messages": [], "timestamps": []}

# AI Chatbot Initialization
chat_model = ChatGoogleGenerativeAI(model=LATEST_GEMINI_MODEL)

# User Input
user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    chat_data["messages"].insert(0, HumanMessage(content=user_input))
    chat_data["timestamps"].insert(0, timestamp)

    chat_history = [msg for msg in chat_data["messages"] if isinstance(msg, AIMessage)]
    response = chat_model.invoke(chat_history + [HumanMessage(content=user_input)])
    response_text = response.content

    chat_data["messages"].insert(1, AIMessage(content=response_text))
    chat_data["timestamps"].insert(1, timestamp)

    save_chats()

# Display Chat Messages
for msg, timestamp in zip(chat_data["messages"], chat_data["timestamps"]):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"[{timestamp}] {msg.content}")
