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

# Custom 3D Styling with CSS
st.markdown(
    """
    <style>
    body { background-color: #121212; color: #e0e0e0; }
    .stApp { background-color: #121212; }
    
    /* 3D Buttons */
    .stButton>button {
        background: linear-gradient(145deg, #1f1f1f, #292929);
        color: white;
        border: none;
        border-radius: 10px;
        box-shadow: 3px 3px 6px #0a0a0a, -3px -3px 6px #333;
        padding: 10px 20px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 4px 4px 8px #000000, -4px -4px 8px #444;
    }

    /* Chat bubbles */
    .stChatMessage {
        background: linear-gradient(145deg, #1e1e1e, #252525);
        padding: 12px;
        border-radius: 10px;
        box-shadow: 3px 3px 5px #0a0a0a, -3px -3px 5px #333;
        margin-bottom: 10px;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        background: #222;
        color: white;
        border: 2px solid #444;
        border-radius: 8px;
        padding: 10px;
        transition: 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #888;
        box-shadow: 0px 0px 5px #888;
    }

    /* Sidebar */
    .stSidebar {
        background-color: #181818;
    }
    .stSidebar .stButton>button {
        background: linear-gradient(145deg, #1c1c1c, #252525);
        color: white;
        box-shadow: 2px 2px 5px #0a0a0a, -2px -2px 5px #333;
    }

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

# Ensure chat data exists
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

# Export Chat as PDF with Better Formatting
def export_pdf(chat_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Chat History", ln=True, align="C")
    pdf.ln(5)

    for role, msg in zip(["User", "AI"] * (len(chat_data["messages"]) // 2), chat_data["messages"]):
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 8, f"{role}:", ln=True)  
        pdf.set_font("Arial", size=11)
        clean_text = msg.content.replace("**", "")  # Remove Markdown Bold Symbols
        pdf.multi_cell(0, 7, clean_text)  # Wraps long messages
        pdf.ln(3)

    pdf_file_path = "chat_history.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

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
        st.markdown(f"[{timestamp}] {msg.content}")
