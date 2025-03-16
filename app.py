import streamlit as st
import json
import pandas as pd
import google.generativeai as genai
import io
import sys
import os
import time
import plotly.express as px
from dotenv import load_dotenv
from fpdf import FPDF
from langchain.schema import AIMessage, HumanMessage  # ✅ Import Messages for Visibility

# ✅ Securely Load API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ Google GenAI API key is missing! Add it to `.env`.")
    st.stop()

# ✅ Configure AI Model
genai.configure(api_key=API_KEY)
MODEL = "gemini-1.5-pro"

# ✅ AI System Instructions (Industry Focus)
SYSTEM_PROMPT = """
You are an AI Data Science Tutor specialized in industry applications:
- Provide structured insights for **Finance, Healthcare, Retail, and Manufacturing**.
- Suggest **best ML models, hyperparameters, and optimizations**.
- Recommend **datasets, tools, and career pathways** for Data Scientists.
- Generate **business reports, visual insights, and AI-powered documentation**.
"""

# ✅ AI Response Generation with Streaming
def get_ai_response(user_input):
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nQuestion: {user_input}")
        return response.text if response and response.text else "⚠️ No response generated."
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
st.sidebar.write(f"👋 Welcome, {st.session_state.username}!")

# ✅ Sidebar - Dark Mode Toggle
st.sidebar.title("⚙️ Settings")
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

# ✅ Apply Dark Mode Styling
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            body { background-color: #1E1E1E; color: white; }
            .stButton>button { background-color: #444; color: white; border-radius: 5px; }
        </style>
    """, unsafe_allow_html=True)

# ✅ Industry-Specific Topics
st.sidebar.title("🏢 Industry Use Cases")
industry = st.sidebar.selectbox("Select Industry", ["Finance", "Healthcare", "Retail", "Manufacturing", "General AI"])

# ✅ Chat Interface
st.title("🧠 AI Data Science Tutor")
user_input = st.chat_input("Ask an industry-specific AI question...")

if user_input:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # ✅ Display Human Message
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.session_state.chat_history.append(("🧑‍💻 **You:**", user_input, timestamp))

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""

        for word in get_ai_response(user_input).split():
            response_text += word + " "
            time.sleep(0.03)
            response_placeholder.markdown(response_text)

    # ✅ Display AI Message
    st.session_state.chat_history.append(AIMessage(content=response_text))
    st.session_state.chat_history.append(("🤖 **AI:**", response_text, timestamp))

    save_chat_history()
    st.rerun()

# ✅ Display Chat History with Timestamps
st.subheader("📜 Chat History")
for role, msg, timestamp in st.session_state.chat_history:
    st.markdown(f"**[{timestamp}] {role}** {msg}")

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

    # ✅ Auto-Generated Visualizations
    st.subheader("📊 AI-Generated Visualization")
    fig = px.histogram(df, x=df.columns[0], title="Data Distribution")
    st.plotly_chart(fig)

# ✅ AI-Powered Resume Evaluator
st.sidebar.title("💼 Job & Resume AI Insights")
resume_text = st.sidebar.text_area("Paste your Resume for AI Analysis")

if st.sidebar.button("🔍 Analyze Resume"):
    ai_resume_feedback = get_ai_response(f"Analyze this resume for a data science job:\n\n{resume_text}")
    st.sidebar.markdown(ai_resume_feedback)

# ✅ Chat History Download as PDF
st.sidebar.title("📥 Export Chat History")
if st.sidebar.button("📄 Download as PDF"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Chat History", ln=True, align="C")
    pdf.ln(5)

    for role, msg, timestamp in st.session_state.chat_history:
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 8, f"[{timestamp}] {role}:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, msg)
        pdf.ln(3)

    pdf_file_path = "chat_history.pdf"
    pdf.output(pdf_file_path)

    with open(pdf_file_path, "rb") as f:
        st.sidebar.download_button("⬇️ Download PDF", data=f, file_name="chat_history.pdf", mime="application/pdf")
        st.sidebar.success("✅ PDF Ready for Download!")
