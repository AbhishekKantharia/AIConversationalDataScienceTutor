import streamlit as st
import os
import json
import time
import datetime
import requests
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from fpdf import FPDF
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

# ✅ File Paths
CHAT_SESSIONS_DIR = "chat_sessions"
BANNED_IPS_FILE = "banned_ips.json"

os.makedirs(CHAT_SESSIONS_DIR, exist_ok=True)

# ✅ Initialize Session State Variables (Fix for KeyError)
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = [file.replace(".json", "") for file in os.listdir(CHAT_SESSIONS_DIR)]
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ✅ Ban IPs for Profanity
PROFANITY_LIST = ["badword1", "badword2", "offensiveword3"]

def get_user_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return response.json()["ip"]
    except:
        return "Unknown"

def load_banned_ips():
    try:
        with open(BANNED_IPS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_banned_ips(banned_ips):
    with open(BANNED_IPS_FILE, "w") as f:
        json.dump(banned_ips, f, indent=4)

def check_profanity(user_input):
    return any(word.lower() in user_input.lower() for word in PROFANITY_LIST)

banned_ips = load_banned_ips()
user_ip = get_user_ip()
if user_ip in banned_ips:
    st.error("🚫 Your IP has been banned for violating community guidelines.")
    st.stop()

# ✅ Load Chat History
def load_chat_history(chat_id):
    filepath = os.path.join(CHAT_SESSIONS_DIR, f"{chat_id}.json")
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_history(chat_id, history):
    filepath = os.path.join(CHAT_SESSIONS_DIR, f"{chat_id}.json")
    with open(filepath, "w") as f:
        json.dump(history, f, indent=4)

# ✅ Streamlit Page Config
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

# ✅ Sidebar: Theme & Settings
st.sidebar.title("⚙️ Settings")
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

if st.session_state.dark_mode:
    st.markdown("""
        <style>
            body { background-color: #1E1E1E; color: white; }
            .stApp { background-color: #1E1E1E; }
            .stButton>button { background-color: #444; color: white; border-radius: 5px; }
        </style>
    """, unsafe_allow_html=True)

# ✅ Sidebar: Multi-Chat Support
st.sidebar.title("📂 Chat Sessions")

if st.sidebar.button("➕ New Chat"):
    new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions.append(new_chat_id)
    save_chat_history(new_chat_id, [])
    st.session_state.current_chat = new_chat_id

chat_names = st.session_state.chat_sessions
if chat_names:
    selected_chat = st.sidebar.radio("💬 Select a Chat", chat_names)
    st.session_state.current_chat = selected_chat

# ✅ Rename Chat Option
if st.session_state.current_chat:
    new_chat_name = st.sidebar.text_input("✏️ Rename Chat", value=st.session_state.current_chat)
    if st.sidebar.button("✅ Save Name"):
        os.rename(
            os.path.join(CHAT_SESSIONS_DIR, f"{st.session_state.current_chat}.json"),
            os.path.join(CHAT_SESSIONS_DIR, f"{new_chat_name}.json")
        )
        st.session_state.chat_sessions.remove(st.session_state.current_chat)
        st.session_state.chat_sessions.append(new_chat_name)
        st.session_state.current_chat = new_chat_name
        st.experimental_rerun()

# ✅ Delete Chat Option
if st.session_state.current_chat and st.sidebar.button("🗑️ Delete Chat"):
    os.remove(os.path.join(CHAT_SESSIONS_DIR, f"{st.session_state.current_chat}.json"))
    st.session_state.chat_sessions.remove(st.session_state.current_chat)
    st.session_state.current_chat = None
    st.experimental_rerun()

# ✅ Load Chat Data
if st.session_state.current_chat:
    chat_data = load_chat_history(st.session_state.current_chat)
else:
    chat_data = []

# ✅ AI Chatbot System
st.title("🧠 AI Data Science Tutor")
user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 🚨 Profanity Detection & Auto-Banning
    if check_profanity(user_input):
        banned_ips.append(user_ip)
        save_banned_ips(banned_ips)
        st.error("🚫 Inappropriate language detected. Your IP has been banned.")
        st.stop()

    # Store User Input
    chat_data.append({"role": "user", "message": user_input, "timestamp": timestamp})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""

        for word in chat_model.invoke([user_input]).content.split():
            response_text += word + " "
            time.sleep(0.03)
            response_placeholder.markdown(response_text)

    # Store AI Response
    chat_data.append({"role": "assistant", "message": response_text, "timestamp": timestamp})
    save_chat_history(st.session_state.current_chat, chat_data)

    st.experimental_rerun()

# ✅ Display Chat History Organized by Date
st.subheader("📜 Chat History")
grouped_chats = {}
for entry in chat_data:
    date = entry["timestamp"].split()[0]
    if date not in grouped_chats:
        grouped_chats[date] = []
    grouped_chats[date].append(entry)

for date, messages in grouped_chats.items():
    st.subheader(f"📅 {date}")
    for entry in messages:
        role_icon = "👤" if entry["role"] == "user" else "🤖"
        with st.chat_message(entry["role"]):
            st.markdown(f"**[{entry['timestamp']}] {role_icon}:** {entry['message']}", unsafe_allow_html=True)

# ✅ Export Chat as PDF
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Chat History", ln=True, align="C")
    pdf.ln(5)

    for date, messages in grouped_chats.items():
        pdf.cell(200, 10, f"📅 {date}", ln=True)
        for entry in messages:
            pdf.cell(200, 10, f"{entry['role'].capitalize()}: {entry['message']}", ln=True)
        pdf.ln(3)

    pdf.output("chat_history.pdf")
    return "chat_history.pdf"

if st.sidebar.button("📥 Export Chat as PDF"):
    pdf_path = export_pdf()
    with open(pdf_path, "rb") as f:
        st.sidebar.download_button(label="⬇️ Download PDF", data=f, file_name="chat_history.pdf", mime="application/pdf")
