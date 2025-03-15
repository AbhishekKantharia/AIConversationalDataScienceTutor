import streamlit as st
import json
import time
import matplotlib.pyplot as plt
import pandas as pd
import google.generativeai as genai
import io
import sys
import graphviz
import random
from dotenv import load_dotenv
import os

# ✅ Securely Fetch API Key
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ Google GenAI API key is missing! Add it to `.streamlit/secrets.toml`.")
    st.stop()

# ✅ Configure Google GenAI
genai.configure(api_key=API_KEY)

# ✅ Load & Save Chat History
CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_history():
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(st.session_state.chat_history, f, indent=4)

# ✅ Initialize Session States
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = "User"
if "ai_speed" not in st.session_state:
    st.session_state.ai_speed = 0.02  # AI typing speed

# ✅ Streamlit Page Config
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

# ✅ Authentication System
if not st.session_state.logged_in:
    st.title("🔑 Login to AI Data Science Tutor")
    username = st.text_input("Enter your username:")
    role = st.selectbox("Select Role:", ["User", "Admin"])
    
    if st.button("Login"):
        if not username:
            st.warning("Please enter your username to proceed.")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()
    st.stop()

st.sidebar.title("🔑 User")
st.sidebar.write(f"👋 Welcome, {st.session_state.username}! ({st.session_state.role})")

# ✅ Apply Dark Mode
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
            body { background-color: #1E1E1E; color: white; }
            .stButton>button { background-color: #444; color: white; border-radius: 5px; }
        </style>
        """, unsafe_allow_html=True
    )

# ✅ Sidebar Settings
st.sidebar.title("⚙️ Settings")
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

# ✅ AI Response Speed Control
st.sidebar.title("⚡ AI Speed Control")
st.session_state.ai_speed = st.sidebar.slider("Set AI Typing Speed:", 0.01, 0.1, st.session_state.ai_speed)

st.sidebar.title("📜 Chat History")
if st.sidebar.button("🗑 Clear Chat History"):
    st.session_state.chat_history = []
    save_chat_history()
if st.sidebar.button("📥 Download Chat History"):
    formatted_chat = "\n".join([f"**{st.session_state.username}:** {q}\n**AI:** {a}" for q, a in st.session_state.chat_history])
    st.sidebar.download_button(label="Download", data=formatted_chat, file_name="chat_history.txt", mime="text/plain")

st.title("🧠 Conversational AI Data Science Tutor")

# ✅ Quick Questions
quick_questions = [
    "What is overfitting in ML?",
    "Explain bias-variance tradeoff.",
    "Types of regression?",
    "Supervised vs. Unsupervised learning?",
]
cols = st.columns(len(quick_questions))
for idx, question in enumerate(quick_questions):
    if cols[idx].button(question):
        st.session_state.chat_history.append((st.session_state.username, question))
        response = get_ai_response(question)
        st.session_state.chat_history.append(("assistant", response))
        save_chat_history()
        st.rerun()

# ✅ Chat UI (with Streaming Response)
st.subheader("🗨 Chat")
chat_container = st.container()
with chat_container:
    for role, text in st.session_state.chat_history:
        st.markdown(f"**{'👤 ' if role == st.session_state.username else '🤖 AI:'}** {text}")

# ✅ AI Chat (Streaming Response)
user_input = st.chat_input("Ask a Data Science question...")
if user_input:
    st.session_state.chat_history.append((st.session_state.username, user_input))
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""

        for word in get_ai_response(user_input).split():
            response_text += word + " "
            time.sleep(st.session_state.ai_speed)  # Dynamic AI typing speed
            response_placeholder.markdown(response_text)

    st.session_state.chat_history.append(("assistant", response_text))
    save_chat_history()
    st.rerun()

# ✅ Python Code Editor
st.sidebar.title("📝 Python Code Editor")
st.session_state.code = st.sidebar.text_area("Write your Python code here:", height=200)

code_col1, code_col2 = st.sidebar.columns([0.5, 0.5])
if code_col1.button("Run Code"):
    st.subheader("📝 Python Code Execution")
    st.code(st.session_state.code, language="python")
    try:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        exec_globals = {}
        exec(st.session_state.code, exec_globals)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        st.subheader("📤 Output:")
        st.code(output, language="python")
        if plt.get_fignums():
            st.subheader("📊 Visualization Output:")
            st.pyplot(plt.gcf())
        st.subheader("🧐 AI Explanation:")
        explanation = get_ai_response(f"Explain this Python code: {st.session_state.code}")
        st.markdown(explanation)
    except Exception as e:
        st.error(f"Error: {e}")
if code_col2.button("Clear Code"):
    st.session_state.code = ""
    st.rerun()

# ✅ Data Science Visualizations
st.sidebar.title("📊 Data Science Visualizations")
visualization_option = st.sidebar.selectbox("Select visualization", ["None", "Decision Tree", "Neural Network", "K-Means Clustering"])
visualizations = {"Decision Tree": "digraph G {A -> B; A -> C;}", "Neural Network": "digraph G {A -> B; B -> C; C -> D;}", "K-Means Clustering": "digraph G {Cluster1 -> Point1; Cluster1 -> Point2; Cluster2 -> Point3;}"}
if visualization_option in visualizations:
    st.graphviz_chart(visualizations[visualization_option])
