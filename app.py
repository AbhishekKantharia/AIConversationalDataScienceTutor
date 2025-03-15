import streamlit as st
import json
import pandas as pd
import google.generativeai as genai
import io
import sys
import os
import time
from dotenv import load_dotenv
from fpdf import FPDF

# ✅ Securely Load API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ Google GenAI API key is missing! Add it to `.env`.")
    st.stop()

# ✅ Configure AI Model
genai.configure(api_key=API_KEY)
MODEL = "gemini-1.5-pro"

# ✅ AI System Instructions (Industry-Specific)
SYSTEM_PROMPT = """
You are an AI Data Science Tutor specialized in industry use cases.
- **Provide structured, real-world answers** with examples from **Finance, Healthcare, Retail, and Manufacturing**.
- **Use clear bullet points and technical insights**.
- **Recommend best practices, tools, and datasets** for solving business challenges.
"""

# ✅ AI Response Generation (Improved)
def get_ai_response(user_input):
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nQuestion: {user_input}")
        return f"### 🔍 AI Insights:\n{response.text.replace('\n', '\n- ')}" if response and response.text else "⚠️ No response generated."
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# ✅ Load & Save Chat History
def load_chat_history():
    try:
        with open("chat_history.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_history():
    with open("chat_history.json", "w") as f:
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
            st.rerun()
    st.stop()

st.sidebar.title("🔑 User")
st.sidebar.write(f"👋 Welcome, {st.session_state.username}! ({st.session_state.role})")

# ✅ Sidebar - Dark Mode Toggle
st.sidebar.title("⚙️ Settings")
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

# ✅ Industry-Specific Topics
st.sidebar.title("🏢 Industry Use Cases")
industry = st.sidebar.selectbox("Select Industry", ["Finance", "Healthcare", "Retail", "Manufacturing", "General AI"])

# ✅ Real-Time Chat Interface
st.title("🧠 Industry AI Data Science Tutor")
user_input = st.chat_input("Ask an industry-specific AI question...")

if user_input:
    st.session_state.chat_history.append((st.session_state.username, user_input))
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""

        for word in get_ai_response(user_input).split():
            response_text += word + " "
            time.sleep(0.03)  # Simulate real-time typing
            response_placeholder.markdown(response_text)

    st.session_state.chat_history.append(("assistant", response_text))
    save_chat_history()
    st.rerun()

# ✅ Industry Insights & Data Analysis
st.sidebar.title("📊 AI-Generated Reports & Insights")
report_type = st.sidebar.selectbox("Generate Report for", ["None", "Financial Forecasting", "Customer Sentiment Analysis", "Market Trends"])

if report_type != "None":
    st.subheader(f"📑 AI Report: {report_type}")
    ai_report = get_ai_response(f"Generate a detailed report on {report_type} in {industry} industry.")
    st.markdown(ai_report)

# ✅ Business Data Upload & AI Insights
st.sidebar.title("📂 Upload Data for AI Analysis")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Uploaded Data Preview")
    st.dataframe(df.head())

    # ✅ AI Data Insights
    st.subheader("🔍 AI Insights on Data")
    ai_data_analysis = get_ai_response(f"Analyze the dataset and provide insights:\n\n{df.head().to_string()}")
    st.markdown(ai_data_analysis)

# ✅ Automated Report PDF Export
if st.sidebar.button("📜 Export AI Report to PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(200, 10, ai_report)
    pdf_file_path = "ai_report.pdf"
    pdf.output(pdf_file_path)
    with open(pdf_file_path, "rb") as f:
        st.sidebar.download_button("⬇️ Download PDF", f, file_name="AI_Report.pdf", mime="application/pdf")

# ✅ Job Market Insights & Resume Analyzer
st.sidebar.title("💼 Job & Resume AI Insights")
resume_text = st.sidebar.text_area("Paste your Resume for AI Analysis")

if st.sidebar.button("🔍 Analyze Resume"):
    ai_resume_feedback = get_ai_response(f"Analyze this resume for a data science job:\n\n{resume_text}")
    st.sidebar.markdown(ai_resume_feedback)

# ✅ Display Chat History
st.subheader("🗨 Chat History")
chat_container = st.container()
with chat_container:
    for role, text in st.session_state.chat_history:
        st.markdown(f"**{'👤 ' if role == st.session_state.username else '🤖 AI:'}** {text}")

if st.sidebar.button("🗑 Clear Chat History"):
    st.session_state.chat_history = []
    save_chat_history()

if st.sidebar.button("📥 Download Chat History"):
    formatted_chat = "\n".join([f"**{st.session_state.username}:** {q}\n**AI:** {a}" for q, a in st.session_state.chat_history])
    st.sidebar.download_button(label="Download", data=formatted_chat, file_name="chat_history.txt", mime="text/plain")
