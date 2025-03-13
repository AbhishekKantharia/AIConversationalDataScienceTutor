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
import time  # For real-time streaming

# Load environment variables securely
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# File Paths
CHAT_SESSIONS_FILE = "chat_sessions.pkl"
LATEST_GEMINI_MODEL = "gemini-1.5-pro-latest"

# Streamlit Page Config
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

# Sidebar - Feature Toggles
st.sidebar.header("⚙️ Live Feature Toggles")
feature_settings = ["dark_mode", "multi_chat", "pdf_export", "chat_summarization"]
default_values = [False, True, True, True]

# Initialize session state for toggles
for feature, default in zip(feature_settings, default_values):
    if feature not in st.session_state:
        st.session_state[feature] = default

# Live Toggle Buttons (Update Immediately)
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.multi_chat = st.sidebar.toggle("💬 Multi-Chat", value=st.session_state.multi_chat)
st.session_state.pdf_export = st.sidebar.toggle("📜 PDF Export", value=st.session_state.pdf_export)
st.session_state.chat_summarization = st.sidebar.toggle("🧠 AI Summarization", value=st.session_state.chat_summarization)

# Apply 3D Styling with Live Theme Updates
st.markdown(
    f"""
    <style>
    body {{ background-color: {'#121212' if st.session_state.dark_mode else '#ffffff'}; color: {'#e0e0e0' if st.session_state.dark_mode else '#000000'}; }}
    .stApp {{ background-color: {'#121212' if st.session_state.dark_mode else '#ffffff'}; }}
    .stButton>button {{
        background: linear-gradient(145deg, #1f1f1f, #292929);
        color: white;
        border: none;
        border-radius: 12px;
        box-shadow: 4px 4px 8px #0a0a0a, -4px -4px 8px #333;
        padding: 12px 24px;
        transition: 0.2s;
    }}
    .stButton>button:hover {{
        transform: scale(1.07);
        box-shadow: 5px 5px 10px #000000, -5px -5px 10px #444;
    }}
    .stChatMessage {{
        background: linear-gradient(145deg, #1e1e1e, #252525);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 4px 4px 8px #0a0a0a, -4px -4px 8px #333;
        margin-bottom: 10px;
    }}
    .stTextInput>div>div>input {{
        background: #222;
        color: white;
        border: 2px solid #555;
        border-radius: 10px;
        padding: 12px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Ensure chat_sessions is initialized
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Ensure current_chat is initialized
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# Multi-Chat Support
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

    # ✏️ Rename Chat Option
    if st.session_state.current_chat:
        new_chat_name = st.sidebar.text_input("✏️ Rename Chat", value=st.session_state.current_chat)
        if st.sidebar.button("✅ Save Name"):
            if new_chat_name and new_chat_name not in st.session_state.chat_sessions:
                st.session_state.chat_sessions[new_chat_name] = st.session_state.chat_sessions.pop(st.session_state.current_chat)
                st.session_state.current_chat = new_chat_name

    # 🗑️ Delete Chat Button
    if st.session_state.current_chat:
        if st.sidebar.button("🗑️ Delete Chat"):
            del st.session_state.chat_sessions[st.session_state.current_chat]
            chat_names = list(st.session_state.chat_sessions.keys())  
            st.session_state.current_chat = chat_names[0] if chat_names else None
            st.experimental_rerun()

# Ensure chat_data exists
chat_data = st.session_state.chat_sessions.get(st.session_state.current_chat, {"messages": [], "timestamps": []})

# AI Chatbot with Real-Time Streaming & Enhanced Formatting
chat_model = ChatGoogleGenerativeAI(model=LATEST_GEMINI_MODEL)
user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_data["messages"].insert(0, HumanMessage(content=user_input))
    chat_data["timestamps"].insert(0, timestamp)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""

        # Generate AI Response
        response = chat_model.invoke([HumanMessage(content=user_input)]).content

        # Format response into structured markdown
        formatted_response = f"""
        **🔍 Key Insights:**  
        - **Main Answer:** {response.split(".")[0]}.  
        - **Supporting Details:** {'. '.join(response.split('.')[1:]) if len(response.split('.')) > 1 else 'N/A'}  
        - **Additional Notes:** AI-generated structured response to improve clarity.  

        **📝 Summary:**  
        ```  
        {response}  
        ```
        """

        # Simulate real-time streaming output
        for word in formatted_response.split():
            response_text += word + " "
            time.sleep(0.04)  # Simulate typing effect
            response_placeholder.markdown(response_text)

    chat_data["messages"].insert(1, AIMessage(content=formatted_response))
    chat_data["timestamps"].insert(1, timestamp)

# Display Chat Messages
for msg, timestamp in zip(chat_data["messages"], chat_data["timestamps"]):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
