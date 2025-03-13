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
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

# Sidebar - Toggle for Dark Mode
st.sidebar.header("⚙️ Settings")
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False  # Default to light mode

st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

# Apply Dark/Light Mode Styling
if st.session_state.dark_mode:
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

# Load Chat Sessions & Banned IPs
def load_banned_ips():
    return pickle.load(open(BANNED_IPS_FILE, "rb")) if os.path.exists(BANNED_IPS_FILE) else set()

def save_banned_ips(banned_ips):
    pickle.dump(banned_ips, open(BANNED_IPS_FILE, "wb"))

def load_chats():
    return pickle.load(open(CHAT_SESSIONS_FILE, "rb")) if os.path.exists(CHAT_SESSIONS_FILE) else {}

def save_chats():
    pickle.dump(st.session_state.chat_sessions, open(CHAT_SESSIONS_FILE, "wb"))

# Function to get user IP & check if banned
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

# Load all chat sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chats()

# Sidebar - Chat Management
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
    if chat_names:
        st.session_state.current_chat = chat_names[0]
    else:
        st.session_state.current_chat = None

# Ensure chat_data is properly initialized
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions[st.session_state.current_chat]
else:
    chat_data = {"messages": [], "timestamps": []}  # Fallback to avoid errors

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

# Function to Export Chat as a Properly Formatted PDF
def export_pdf(chat_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)  # Prevents text cutoff
    pdf.add_page()
    pdf.set_font("Arial", style='', size=12)

    pdf.cell(200, 10, "Chat History", ln=True, align="C")
    pdf.ln(5)  # Adds a little space

    for role, msg in zip(["User", "AI"] * (len(chat_data["messages"]) // 2), chat_data["messages"]):
        pdf.set_font("Arial", style='B', size=12)  # Bold for roles
        pdf.cell(0, 8, f"{role}:", ln=True)  

        pdf.set_font("Arial", size=11)  # Regular font for messages
        pdf.multi_cell(0, 7, msg.content)  # Wraps long messages
        pdf.ln(3)  # Adds space between messages

    # Save the PDF as a file
    pdf_file_path = "chat_history.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path  # Return file path for download

# Button to Export Chat as PDF
if st.sidebar.button("📥 Export as PDF"):
    pdf_path = export_pdf(chat_data)
    with open(pdf_path, "rb") as f:
        st.sidebar.download_button(label="⬇️ Download PDF", data=f, file_name="chat_history.pdf", mime="application/pdf")
        st.sidebar.success("✅ PDF is ready for download!")

# Display Chat Messages
for msg, timestamp in zip(chat_data["messages"], chat_data["timestamps"]):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
