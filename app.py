import streamlit as st
import json
import os
import time
import datetime
import pandas as pd
import google.generativeai as genai
import requests
import plotly.express as px
from dotenv import load_dotenv
from fpdf import FPDF
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# ✅ Load API Key Securely
load_dotenv()
API_KEY = os.getenv("google_token")
if not API_KEY:
    st.error("⚠️ Google GenAI API key is missing! Add it to `.env`.")
    st.stop()

# ✅ Configure AI Model
genai.configure(api_key=API_KEY)
MODEL = "gemini-1.5-pro"

# ✅ AI System Prompt
SYSTEM_PROMPT = SystemMessage(
    content="""You are an AI Data Science Tutor specialized in industry applications.
- Provide structured responses using headings, bullet points, and code blocks.
- Cover Finance, Healthcare, Retail, and Manufacturing industries.
- Offer insights on ML models, optimizations, datasets, and career advice.
"""
)

# ✅ AI Response Generation (Structured)
def get_ai_response(user_input):
    try:
        model = ChatGoogleGenerativeAI(model=MODEL, google_api_key=API_KEY)
        response = model.invoke([SYSTEM_PROMPT, HumanMessage(content=user_input)])
        if response and response.content:
            return response.content.strip()
        return "⚠️ No response generated."
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# ✅ Load & Save Chat History
CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        return []
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
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
if "code" not in st.session_state:
    st.session_state.code = ""

# ✅ Streamlit Page Config
st.set_page_config(page_title="Industry AI Data Science Tutor", page_icon="🤖", layout="wide")

# ✅ Authentication System
if not st.session_state.logged_in:
    st.title("🔑 Login to AI Data Science Tutor")
    username = st.text_input("Enter your username:")
    role = st.selectbox("Select Role:", ["User", "Admin", "Business Analyst", "Data Scientist"])
    
    if st.button("Login"):
        if not username:
            st.warning("Please enter your username to proceed.")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.session_state.chat_history = load_chat_history()
            st.rerun()
    st.stop()

st.sidebar.title("🔑 User")
st.sidebar.write(f"👋 Welcome, {st.session_state.username}!")

# ✅ Sidebar - Dark Mode Toggle
st.sidebar.title("⚙️ Settings")
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

# Apply Dark Mode Styling
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        body { background-color: #1E1E1E; color: white; }
        .stApp { background-color: #1E1E1E; }
        .stButton>button { background-color: #444; color: white; border-radius: 5px; }
        </style>
        """, unsafe_allow_html=True
    )

# ✅ Sidebar - Chat History Actions
st.sidebar.title("📜 Chat History")
if st.sidebar.button("🗑 Clear Chat History"):
    st.session_state.chat_history = []
    save_chat_history()
if st.sidebar.button("📥 Download Chat History"):
    formatted_chat = "\n".join([f"**{entry['username']} ({entry['role']}):** {entry['message']}" for entry in st.session_state.chat_history])
    st.sidebar.download_button(label="Download", data=formatted_chat, file_name="chat_history.txt", mime="text/plain")

st.title("🧠 AI Data Science Tutor")

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
        st.session_state.chat_history.append({"username": st.session_state.username, "role": st.session_state.role, "message": question, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        response = get_ai_response(question)
        st.session_state.chat_history.append({"username": "AI Assistant", "role": "AI", "message": response, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        save_chat_history()
        st.rerun()

# ✅ Chat Interface with Streaming Response
user_input = st.chat_input("Ask an industry-specific AI question...")
if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.chat_history.append({"username": st.session_state.username, "role": st.session_state.role, "message": user_input, "timestamp": timestamp})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""
        ai_response = get_ai_response(user_input)
        for word in ai_response.split():
            response_text += word + " "
            time.sleep(0.03)
            response_placeholder.markdown(response_text, unsafe_allow_html=True)
            
    st.session_state.chat_history.append({"username": "AI Assistant", "role": "AI", "message": response_text, "timestamp": timestamp})
    save_chat_history()
    st.rerun()

# ✅ Display Chat History Grouped by Date
st.subheader("📜 Chat History")
# Group messages by date
grouped = {}
for entry in st.session_state.chat_history:
    date = entry["timestamp"].split()[0]
    if date not in grouped:
        grouped[date] = []
    grouped[date].append(entry)

for date, messages in grouped.items():
    st.subheader(f"📅 {date}")
    for entry in messages:
        role_icon = "👤" if entry["role"].lower() != "ai" else "🤖"
        with st.chat_message(entry["role"].lower()):
            st.markdown(f"**[{entry['timestamp']}] {role_icon} {entry['username']}:**\n\n{entry['message']}", unsafe_allow_html=True)

# ✅ Business Data Upload & AI Insights
st.sidebar.title("📂 Upload Data for AI Analysis")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Uploaded Data Preview")
    st.dataframe(df.head())
    
    st.subheader("🔍 AI Insights on Data")
    ai_data_analysis = get_ai_response(f"Analyze this dataset:\n\n{df.head().to_string()}")
    st.markdown(ai_data_analysis)
    
    # Auto-Generated Visualizations
    st.subheader("📊 AI-Generated Visualization")
    fig = px.histogram(df, x=df.columns[0], title="Data Distribution")
    st.plotly_chart(fig)

# ✅ AI-Powered Resume Evaluator
st.sidebar.title("💼 Job & Resume AI Insights")
resume_text = st.sidebar.text_area("Paste your Resume for AI Analysis")
if st.sidebar.button("🔍 Analyze Resume"):
    ai_resume_feedback = get_ai_response(f"Analyze this resume for a data science job:\n\n{resume_text}")
    st.sidebar.markdown(ai_resume_feedback)

# ✅ Export Chat History as PDF
def export_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Chat History", ln=True, align="C")
    pdf.ln(5)
    for entry in st.session_state.chat_history:
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 8, f"[{entry['timestamp']}] {entry['username']} ({entry['role']}):", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, entry['message'])
        pdf.ln(3)
    pdf_file_path = "chat_history.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

if st.sidebar.button("📥 Export Chat as PDF"):
    pdf_path = export_pdf()
    with open(pdf_path, "rb") as f:
        st.sidebar.download_button(label="⬇️ Download PDF", data=f, file_name="chat_history.pdf", mime="application/pdf")
        st.sidebar.success("✅ PDF is ready for download!")
