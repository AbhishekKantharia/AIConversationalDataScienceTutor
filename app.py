import streamlit as st
import json
import os
import time
import datetime
import google.generativeai as genai
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# ✅ Load API Key from Streamlit Secrets
load_dotenv()
API_KEY = os.getenv("google_token")

if not API_KEY:
    st.error("⚠️ **API Key Missing**. Add `google_token` to your `.env` file.")
    st.stop()

# ✅ Configure AI Model
genai.configure(api_key=API_KEY)
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=API_KEY)

# ✅ Profanity Words List
PROFANITY_WORDS = {"badword1", "badword2", "badword3"}  # Add actual words

# ✅ Function to Detect Profanity
def contains_profanity(text):
    return any(word in text.lower() for word in PROFANITY_WORDS)

# ✅ Function to Get User IP
def get_user_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return response.json().get("ip", "Unknown")
    except:
        return "Unknown"

# ✅ Ban System
BANNED_IPS_FILE = "banned_ips.json"

def load_banned_ips():
    if os.path.exists(BANNED_IPS_FILE):
        with open(BANNED_IPS_FILE, "r") as f:
            return json.load(f)
    return []

def save_banned_ip(ip):
    banned_ips = load_banned_ips()
    if ip not in banned_ips:
        banned_ips.append(ip)
        with open(BANNED_IPS_FILE, "w") as f:
            json.dump(banned_ips, f)

# ✅ Check if User is Banned
user_ip = get_user_ip()
if user_ip in load_banned_ips():
    st.error("🚫 **You have been banned for inappropriate behavior.**")
    st.stop()

# ✅ Initialize Session States
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "multi_chat" not in st.session_state:
    st.session_state.multi_chat = True
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# ✅ Streamlit Page Config
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

# ✅ Dark Mode Toggle
st.sidebar.header("⚙️ Settings")
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

# ✅ Apply Dark Mode Styling
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        body { background-color: #121212; color: white; }
        .stApp { background-color: #121212; }
        .stButton>button { background-color: #333; color: white; border-radius: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Chat Session Management
st.sidebar.header("💬 Chat Sessions")

# ✅ Create New Chat
if st.sidebar.button("➕ New Chat"):
    chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions[chat_id] = {"messages": [], "timestamps": []}
    st.session_state.current_chat = chat_id

# ✅ Select Existing Chat
chat_names = list(st.session_state.chat_sessions.keys())
if chat_names:
    selected_chat = st.sidebar.radio("📌 Select a Chat", chat_names)
    st.session_state.current_chat = selected_chat

# ✅ Rename Chat
if st.session_state.current_chat:
    new_chat_name = st.sidebar.text_input("✏️ Rename Chat", value=st.session_state.current_chat)
    if st.sidebar.button("✅ Save Name"):
        if new_chat_name and new_chat_name not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[new_chat_name] = st.session_state.chat_sessions.pop(st.session_state.current_chat)
            st.session_state.current_chat = new_chat_name

# ✅ Delete Chat
if st.session_state.current_chat and st.sidebar.button("🗑 Delete Chat"):
    del st.session_state.chat_sessions[st.session_state.current_chat]
    st.session_state.current_chat = chat_names[0] if chat_names else None
    st.experimental_rerun()

# ✅ Fetch Chat History
def get_chat_history():
    if st.session_state.current_chat:
        return st.session_state.chat_sessions[st.session_state.current_chat].get("messages", [])
    return []

# ✅ Chat Prompt Template (Fixing `history` issue)
chat_prompt = ChatPromptTemplate(
    messages=[
        ("system", "You are a helpful AI Data Science Tutor. Respond professionally."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}"),
    ]
)
output_parser = StrOutputParser()

# ✅ Function to Get AI Response
def get_ai_response(user_input):
    history = get_chat_history()
    
    try:
        response = chat_model.invoke([chat_prompt.format(user_input=user_input, history=history)])
        return response.content if response else "⚠️ AI could not generate a response."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ✅ Chat History with Date Timelines
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions[st.session_state.current_chat]
    
    # ✅ Display Messages by Date
    st.title(f"📅 {st.session_state.current_chat}")
    grouped_messages = {}
    for msg, timestamp in zip(chat_data["messages"], chat_data["timestamps"]):
        date = timestamp.split()[0]
        if date not in grouped_messages:
            grouped_messages[date] = []
        grouped_messages[date].append((msg, timestamp))
    
    for date, messages in grouped_messages.items():
        st.subheader(f"📅 {date}")
        for msg, timestamp in messages:
            role = "👤 User" if isinstance(msg, str) else "🤖 AI"
            with st.chat_message(role):
                st.markdown(f"**[{timestamp}] {role}:** {msg}")

# ✅ User Input
user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ✅ Check for Profanity
    if contains_profanity(user_input):
        save_banned_ip(user_ip)
        st.error("🚫 **You have been banned for using inappropriate language.**")
        st.stop()

    # ✅ Append User Message
    st.session_state.chat_sessions[st.session_state.current_chat]["messages"].append(user_input)
    st.session_state.chat_sessions[st.session_state.current_chat]["timestamps"].append(timestamp)

    # ✅ Get AI Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""

        for word in get_ai_response(user_input).split():
            response_text += word + " "
            time.sleep(0.03)
            response_placeholder.markdown(response_text)

    # ✅ Append AI Response
    st.session_state.chat_sessions[st.session_state.current_chat]["messages"].append(response_text)
    st.session_state.chat_sessions[st.session_state.current_chat]["timestamps"].append(timestamp)
    
    st.rerun()
