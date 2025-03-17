import streamlit as st
import time
import json
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# ✅ Load API Key Securely
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ **API KEY not found**❗❗❗ Please add your Google API key to the `.env` file.")
    st.stop()

# ✅ Initialize Google API and AI Model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

# ✅ Chat History Functions
CHAT_DIR = "chat_history"
os.makedirs(CHAT_DIR, exist_ok=True)

def get_chat_history(username):
    """Load chat history from a file."""
    try:
        with open(f"{CHAT_DIR}/{username}.json", "r") as hfile:
            return json.load(hfile)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_chat_history(username):
    """Save chat history to a file."""
    with open(f"{CHAT_DIR}/{username}.json", "w") as hfile:
        json.dump(st.session_state.chat_history, hfile, indent=4)

def delete_chat_history(username):
    """Delete chat history for a user."""
    try:
        os.remove(f"{CHAT_DIR}/{username}.json")
        st.session_state.chat_history = []
        st.success("✅ Chat history deleted successfully.")
    except FileNotFoundError:
        st.warning("⚠️ No chat history found to delete.")

def download_chat_history(username):
    """Download chat history as a text file."""
    chat_history = get_chat_history(username)
    if chat_history:
        chat_text = "\n".join([f"User: {chat['user']}\nAI: {chat['ai']}\n" for chat in chat_history])
        st.download_button(
            label="⬇️ Download Chat History",
            data=chat_text,
            file_name=f"{username}_chat_history.txt",
            mime="text/plain"
        )
    else:
        st.warning("⚠️ No chat history available to download.")

# ✅ Streamlit Page Config
st.set_page_config(page_title="Data Science AI Tutor", page_icon="🤖", layout="centered")

# ✅ User Authentication
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🤖 Data Science Tutor")
    username = st.text_input("Enter your username:")
    if st.button("Login"):
        if not username:
            st.error("⚠️ Please enter a username.")
        else:
            st.session_state.name = username
            st.session_state.login = True
            st.session_state.chat_history = get_chat_history(username)
            st.success("✅ Chat history loaded!" if st.session_state.chat_history else "🆕 New session started.")
            time.sleep(1)
            st.rerun()
    st.stop()

# ✅ Sidebar for User Info and Chat Controls
username = st.session_state.name
with st.sidebar:
    st.write(f"### 👋 Hello, {username.title()}! 🎉")
    st.write("""
#### Welcome to the AI Data Science Tutor 🤖
I can help with:
- 🧠 Machine Learning
- 📊 Data Analysis & Visualization
- 🤖 AI & Deep Learning
- 📝 Python for Data Science
""")
    if st.button("🗑 Delete Chat History"):
        delete_chat_history(username)
    download_chat_history(username)

# ✅ Display Chat History
if not st.session_state.chat_history:
    st.chat_message("assistant").write("💡 **Tip:** Ask me anything related to **data science**!")
else:
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(f"**🧑‍💻 User:** {chat['user']}")
        with st.chat_message("assistant"):
            st.markdown(f"**🤖 AI:** {chat['ai']}")

# ✅ AI Chat Prompt Template
chat_prompt = ChatPromptTemplate(
    messages=[
        ("system", """
        You are a Data Science AI Tutor. Your job is to:
        - Answer **ONLY** data science-related questions.
        - Provide structured answers with **examples, bullet points, and code snippets** if needed.
        - If a question is **not related** to data science, respond with:
          "I am unable to answer that question. Please ask something related to data science."
        """),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}")
    ],
)

# ✅ AI Processing Chain
output_parser = StrOutputParser()
runnable_get_history = RunnableLambda(get_chat_history)
chain = RunnablePassthrough.assign(history=runnable_get_history) | chat_prompt | chat_model | output_parser

# ✅ Chat Input with Streaming AI Response
user_input = st.chat_input("💬 Ask a Data Science question...")

if user_input:
    with st.chat_message("user"):
        st.markdown(f"**🧑‍💻 User:** {user_input}")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""
        
        with st.spinner("🤔 AI is thinking..."):
            try:
                ai_response = chain.invoke({"user_input": user_input})
                for word in ai_response.split():
                    response_text += word + " "
                    time.sleep(0.03)  # Simulate real-time typing
                    response_placeholder.markdown(response_text)

                # Save chat history
                st.session_state.chat_history.append({"user": user_input, "ai": response_text})
                save_chat_history(username)
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ AI Error: {e}")
