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

# Apply 3D Styling with CSS
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
        border-radius: 12px;
        box-shadow: 4px 4px 8px #0a0a0a, -4px -4px 8px #333;
        padding: 12px 24px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.07);
        box-shadow: 5px 5px 10px #000000, -5px -5px 10px #444;
    }

    /* 3D Chat Bubbles */
    .stChatMessage {
        background: linear-gradient(145deg, #1e1e1e, #252525);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 4px 4px 8px #0a0a0a, -4px -4px 8px #333;
        margin-bottom: 10px;
    }

    /* 3D Inputs */
    .stTextInput>div>div>input {
        background: #222;
        color: white;
        border: 2px solid #555;
        border-radius: 10px;
        padding: 12px;
        transition: 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #888;
        box-shadow: 0px 0px 7px #888;
    }

    /* Sidebar */
    .stSidebar {
        background-color: #181818;
    }
    .stSidebar .stButton>button {
        background: linear-gradient(145deg, #1c1c1c, #252525);
        color: white;
        box-shadow: 3px 3px 6px #0a0a0a, -3px -3px 6px #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Export Chat as PDF (if enabled)
if st.session_state.pdf_export:
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
            clean_text = msg.content.replace("**", "")
            pdf.multi_cell(0, 7, clean_text)
            pdf.ln(3)

        pdf_file_path = "chat_history.pdf"
        pdf.output(pdf_file_path)
        return pdf_file_path

    if st.sidebar.button("📥 Export as PDF"):
        pdf_path = export_pdf(chat_data)
        with open(pdf_path, "rb") as f:
            st.sidebar.download_button(label="⬇️ Download PDF", data=f, file_name="chat_history.pdf", mime="application/pdf")
            st.sidebar.success("✅ PDF is ready for download!")

# Ensure chat_data is properly initialized
# Ensure chat_sessions is initialized
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Ensure current_chat is initialized
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# Multi-Chat Support (if enabled)
if st.session_state.multi_chat:
    st.sidebar.header("📂 Chat Sessions")

    if st.sidebar.button("➕ New Chat"):
        new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_chat_id] = {"messages": [], "timestamps": []}
        st.session_state.current_chat = new_chat_id

    chat_names = list(st.session_state.chat_sessions.keys())
    if chat_names:
        selected_chat = st.sidebar.radio("💬 Select a Chat", chat_names)
        st.session_state.current_chat = selected_chat

    if st.session_state.current_chat is None and chat_names:
        st.session_state.current_chat = chat_names[0]

# Ensure chat_data is always available
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions.get(st.session_state.current_chat, {"messages": [], "timestamps": []})
else:
    chat_data = {"messages": [], "timestamps": []}  # Default if no chat exists

# Ensure chat_data is always available
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions.get(st.session_state.current_chat, {"messages": [], "timestamps": []})
else:
    chat_data = {"messages": [], "timestamps": []}  # Default if no chat exists


# Initialize chat_data safely
if st.session_state.current_chat and st.session_state.multi_chat:
    chat_data = st.session_state.chat_sessions[st.session_state.current_chat]
else:
    chat_data = {"messages": [], "timestamps": []}  # Fallback if multi-chat is disabled

# Display Chat Messages
for msg, timestamp in zip(chat_data["messages"], chat_data["timestamps"]):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"[{timestamp}] {msg.content}")
