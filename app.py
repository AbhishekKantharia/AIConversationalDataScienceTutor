import streamlit as st
import time
import json
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import datetime

# ✅ Load API Key Securely
load_dotenv()
API_KEY = os.getenv("google_token")

if not API_KEY:
    st.error("⚠️ **API KEY not found!** Please add your Google API key to the `.env` file.")
    st.stop()

# ✅ Configure AI Model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=API_KEY)

# ✅ Chat History Functions
def get_chat_history(username):
    """ Load user-specific chat history from a JSON file. """
    try:
        with open(f"chat_history/{username}.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_chat_history(username):
    """ Save chat history to a JSON file. """
    os.makedirs("chat_history", exist_ok=True)
    with open(f"chat_history/{username}.json", "w") as file:
        json.dump(st.session_state.chat_history, file, indent=4)

def delete_chat_history(username):
    """ Delete chat history file. """
    try:
        os.remove(f"chat_history/{username}.json")
        st.session_state.chat_history = []
        st.success("✅ Chat history deleted successfully.")
    except FileNotFoundError:
        st.warning("⚠️ No chat history found to delete.")

def download_chat_history(username):
    """ Provide an option to download the chat history as a text file. """
    chat_history = get_chat_history(username)
    if chat_history:
        chat_text = "\n".join([f"User: {entry['user']}\nAI: {entry['ai']}\n" for entry in chat_history])
        st.download_button(
            label="📥 Download Chat History",
            data=chat_text,
            file_name=f"{username}_chat_history.txt",
            mime="text/plain"
        )
    else:
        st.warning("⚠️ No chat history available to download.")

# ✅ Streamlit Page Config
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="centered")

# ✅ Authentication System
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔑 AI Data Science Tutor")
    username = st.text_input(label="Enter your username")
    role = st.selectbox("Select Role:", ["User", "Admin"])

    if st.button("Login"):
        if not username:
            st.error("⚠️ Please enter a username.")
        else:
            st.session_state.name = username
            st.session_state.role = role
            st.session_state.login = True
            st.session_state.chat_history = get_chat_history(username)
            
            st.success("✅ Chat history loaded successfully." if st.session_state.chat_history else "✅ New session started.")
            time.sleep(1)
            st.rerun()
    st.stop()

username = st.session_state.name
role = st.session_state.role

# ✅ Sidebar - User Info & Actions
with st.sidebar:
    st.title("🤖 AI Data Science Tutor")
    st.write(f"👋 Welcome, **{username.title()}**! 🎉 ({role})")
    st.write("""
I’m here to help you with all things related to **Data Science**:
- 📊 Machine Learning  
- 📈 Data Visualization  
- 📡 AI Algorithms  
- 🐍 Python for Data Science  
...and much more! 🚀
""")

    if st.button("🗑 Delete Chat History"):
        delete_chat_history(username)

    download_chat_history(username)

# ✅ Chat Prompt Template
chat_prompt = ChatPromptTemplate(
    messages=[
        ("system", """You are a professional AI Data Science Tutor.
        - Answer only data science-related questions.
        - If a question is **not** related to data science, respond with:
        "I can only assist with Data Science topics. Please ask something relevant."
        """),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}"),
    ]
)

output_parser = StrOutputParser()
runnable_get_history = RunnableLambda(get_chat_history)
chain = RunnablePassthrough.assign(history=runnable_get_history) | chat_prompt | chat_model | output_parser

# ✅ Display Chat History
if not get_chat_history(username):
    st.chat_message("assistant").write("Feel free to ask anything about **Data Science**! 😊")
else:
    for entry in get_chat_history(username):
        timestamp = entry.get("timestamp", "Unknown Time")
        with st.chat_message("user"):
            st.markdown(f"🕒 **{timestamp}**\n👤 **User:** {entry['user']}")
        with st.chat_message("assistant"):
            st.markdown(f"🕒 **{timestamp}**\n🤖 **AI:** {entry['ai']}")

# ✅ Chat Input
user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.chat_history.append({"user": user_input, "ai": "", "timestamp": timestamp})

    with st.chat_message("user"):
        st.markdown(f"🕒 **{timestamp}**\n👤 **User:** {user_input}")

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            try:
                response = chain.invoke({"user_input": user_input})
                st.markdown(f"🕒 **{timestamp}**\n🤖 **AI:** {response}")

                st.session_state.chat_history[-1]["ai"] = response
                save_chat_history(username)

                st.rerun()

            except Exception as e:
                st.error(f"⚠️ **Error:** {e}")
