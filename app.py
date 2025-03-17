import streamlit as st
import time
import json
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import os
import datetime
import requests
from dotenv import load_dotenv

# ✅ Load API Key Securely
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ Google GenAI API key is missing! Add it to `.env`.")
    st.stop()

# ✅ Configure AI Model
genai.configure(api_key=API_KEY)
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=API_KEY)

# ✅ Profanity Detection List
PROFANITY_LIST = ["badword1", "badword2", "offensivephrase"]  # Add more words

# ✅ IP Auto-Banning System
def get_user_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return response.json()["ip"]
    except:
        return "Unknown"

BANNED_IPS_FILE = "banned_ips.json"

def load_banned_ips():
    try:
        with open(BANNED_IPS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_banned_ips(banned_ips):
    with open(BANNED_IPS_FILE, "w") as f:
        json.dump(banned_ips, f, indent=4)

# ✅ Check & Ban IP if Profanity Detected
user_ip = get_user_ip()
banned_ips = load_banned_ips()

if user_ip in banned_ips:
    st.error("🚫 Your IP has been banned for inappropriate language.")
    st.stop()

# ✅ Chat Management Functions
CHAT_DIR = "chat_sessions"

def get_chat_history(username):
    chat_file = os.path.join(CHAT_DIR, f"{username}.json")
    try:
        with open(chat_file, "r") as hfile:
            return json.load(hfile)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_chat_history(username, chat_data):
    os.makedirs(CHAT_DIR, exist_ok=True)
    chat_file = os.path.join(CHAT_DIR, f"{username}.json")
    with open(chat_file, "w") as hfile:
        json.dump(chat_data, hfile, indent=4)

# ✅ Dark Mode Toggle
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

if st.session_state.dark_mode:
    st.markdown("""
        <style>
            body { background-color: #1E1E1E; color: white; }
            .stApp { background-color: #1E1E1E; }
            .stButton>button { background-color: #444; color: white; border-radius: 5px; }
        </style>
    """, unsafe_allow_html=True)

# ✅ Authentication System
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔑 Login to AI Data Science Tutor")
    username = st.text_input("Enter your username:")
    
    if st.button("Login"):
        if not username:
            st.error("Please enter a username.")
        else:
            st.session_state.username = username
            st.session_state.logged_in = True
            st.session_state.chat_history = get_chat_history(username)
            st.rerun()
    st.stop()

username = st.session_state.username
st.sidebar.write(f"👋 Welcome, {username}!")

# ✅ Multi-Chat System
if "current_chat" not in st.session_state:
    st.session_state.current_chat = f"Chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

st.sidebar.subheader("📂 Chat Sessions")
chat_names = os.listdir(CHAT_DIR) if os.path.exists(CHAT_DIR) else []

if chat_names:
    selected_chat = st.sidebar.radio("Select Chat", chat_names)
    st.session_state.current_chat = selected_chat.replace(".json", "")

if st.sidebar.button("➕ New Chat"):
    new_chat = f"Chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.current_chat = new_chat
    save_chat_history(new_chat, [])
    st.rerun()

if st.sidebar.button("🗑 Delete Current Chat"):
    chat_path = os.path.join(CHAT_DIR, f"{st.session_state.current_chat}.json")
    os.remove(chat_path)
    st.success("Chat deleted successfully!")
    st.rerun()

# ✅ Chat Interface
st.title("🧠 AI Data Science Tutor")

# ✅ Display Chat History (Sorted by Date)
chat_history = get_chat_history(st.session_state.current_chat)

sorted_chats = {}
for entry in chat_history:
    date = entry["timestamp"].split()[0]
    if date not in sorted_chats:
        sorted_chats[date] = []
    sorted_chats[date].append(entry)

for date, messages in sorted_chats.items():
    st.subheader(f"📅 {date}")
    for chat in messages:
        role_icon = "👤" if chat["role"] == "user" else "🤖"
        with st.chat_message(chat["role"]):
            st.markdown(f"**{role_icon} {chat['role'].title()}**\n\n{chat['message']}")

# ✅ AI Response Handling
def contains_profanity(text):
    return any(word in text.lower() for word in PROFANITY_LIST)

user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if contains_profanity(user_input):
        banned_ips.append(user_ip)
        save_banned_ips(banned_ips)
        st.error("🚫 Profanity detected! Your IP has been banned.")
        st.stop()

    chat_history.append({"role": "user", "message": user_input, "timestamp": timestamp})
    save_chat_history(st.session_state.current_chat, chat_history)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            response = chat_model.invoke(user_input)
            chat_history.append({"role": "assistant", "message": response.content, "timestamp": timestamp})
            save_chat_history(st.session_state.current_chat, chat_history)
            st.markdown(f"**🤖 AI:**\n\n{response.content}")

    st.rerun()
