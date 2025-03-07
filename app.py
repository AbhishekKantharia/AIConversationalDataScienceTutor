import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
import google.generativeai as genai
import datetime
import os
import pickle

# Set API Key
genai.configure(api_key="your_actual_api_key_here")

# Streamlit UI Setup
st.set_page_config(page_title="AI Data Science Tutor", layout="wide")
st.title("🤖 AI Data Science Tutor - Powered by Google Gemini")
st.markdown("Ask me anything about **Data Science!** I support **multi-turn conversations.**")

# File to store chat sessions persistently
CHAT_SESSIONS_FILE = "chat_sessions.pkl"

# Function to load chat sessions
def load_chats():
    if os.path.exists(CHAT_SESSIONS_FILE):
        with open(CHAT_SESSIONS_FILE, "rb") as f:
            return pickle.load(f)
    return {}

# Function to save chat sessions
def save_chats():
    with open(CHAT_SESSIONS_FILE, "wb") as f:
        pickle.dump(st.session_state.chat_sessions, f)

# Load all chat sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chats()

# Sidebar - Chat Management
st.sidebar.header("📂 Chat Sessions")

# Create a new chat
if st.sidebar.button("➕ New Chat"):
    new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions[new_chat_id] = {"messages": [], "timestamps": [], "model": "gemini-1.5-pro"}
    st.session_state.current_chat = new_chat_id
    save_chats()

# Select existing chat
chat_names = list(st.session_state.chat_sessions.keys())
if chat_names:
    selected_chat = st.sidebar.radio("💬 Select a Chat", chat_names)
    st.session_state.current_chat = selected_chat

# Ensure there's a selected chat
if "current_chat" not in st.session_state or st.session_state.current_chat not in st.session_state.chat_sessions:
    if chat_names:
        st.session_state.current_chat = chat_names[0]
    else:
        st.session_state.current_chat = None

# Sidebar - Choose Gemini Model
st.sidebar.header("🚀 Select Google Model")
selected_model = st.sidebar.radio("Choose a model:", ["gemini-pro", "gemini-1.5-pro"])
if st.session_state.current_chat:
    st.session_state.chat_sessions[st.session_state.current_chat]["model"] = selected_model

# Ensure the selected chat session exists
if st.session_state.current_chat:
    chat_data = st.session_state.chat_sessions[st.session_state.current_chat]
    messages = chat_data["messages"]
    timestamps = chat_data["timestamps"]
    model_name = chat_data["model"]
else:
    st.warning("Please create a new chat to start chatting!")
    st.stop()

# Initialize Chat Model with Selected Gemini Version
chat_model = ChatGoogleGenerativeAI(model=model_name)

# Function to check if the question is related to Data Science
def is_data_science_question(question):
    keywords = ["data science", "machine learning", "AI", "deep learning", "statistics",
                "Python", "NumPy", "Pandas", "Matplotlib", "scikit-learn", "neural networks",
                "clustering", "regression", "classification", "time series", "data preprocessing"]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in keywords)

# User Input
user_input = st.chat_input("Ask me a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append User Message & Timestamp
    messages.insert(0, HumanMessage(content=user_input))
    timestamps.insert(0, timestamp)

    # Check if the question is related to Data Science
    if not is_data_science_question(user_input):
        response_text = "I'm here to assist with Data Science topics only. Please ask a Data Science-related question."
    else:
        # Retrieve Chat History
        chat_history = [msg for msg in messages if isinstance(msg, AIMessage)]
        
        # Generate AI Response
        response = chat_model.predict_messages(chat_history + [HumanMessage(content=user_input)])
        response_text = response.content

    # Append AI Response & Timestamp
    response_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.insert(1, AIMessage(content=response_text))
    timestamps.insert(1, response_timestamp)

    # Save chat session
    save_chats()

# Display Chat History (User Messages First)
for msg, timestamp in zip(messages, timestamps):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
