import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory  # Memory Support
import google.generativeai as genai
import datetime
import os
import time  # For real-time streaming
from dotenv import load_dotenv  # Secure password storage

# Load environment variables securely
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Streamlit Page Config
st.set_page_config(page_title="AI Data Science Tutor", page_icon="🤖", layout="wide")

# Sidebar - Feature Toggles
st.sidebar.header("⚙️ Live Feature Toggles")
st.session_state.memory_enabled = st.sidebar.toggle("🔁 Enable Memory", value=True)
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

# Apply 3D Styling with Live Theme Updates
st.markdown(
    f"""
    <style>
    body {{ background-color: {'#121212' if st.session_state.dark_mode else '#ffffff'}; color: {'#e0e0e0' if st.session_state.dark_mode else '#000000'}; }}
    .stApp {{ background-color: {'#121212' if st.session_state.dark_mode else '#ffffff'}; }}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize memory if enabled
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Ensure chat_sessions is initialized
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Ensure current_chat is initialized
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
    st.session_state.chat_sessions[st.session_state.current_chat] = {"messages": [], "timestamps": []}

# AI Chatbot with Real-Time Streaming & Memory Toggle
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
user_input = st.chat_input("Ask a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Retrieve chat history if memory is enabled
    chat_history = st.session_state.memory.load_memory_variables({})["chat_history"] if st.session_state.memory_enabled else []

    # Generate AI Response **(only one response per prompt)**
    response = chat_model.invoke(chat_history + [HumanMessage(content=user_input)]).content

    # Store conversation in memory if enabled
    if st.session_state.memory_enabled:
        st.session_state.memory.save_context({"input": user_input}, {"output": response})

    # Append User Message
    st.session_state.chat_sessions[st.session_state.current_chat]["messages"].append(HumanMessage(content=user_input))
    st.session_state.chat_sessions[st.session_state.current_chat]["timestamps"].append(timestamp)

    # **Format AI Response - Eliminating `##` and Enhancing Readability**
    formatted_response = f"""
    **🧠 Answer:** {response.split(".")[0]}.  

    **📌 Key Points:**  
    - {'. '.join(response.split('.')[1:]) if len(response.split('.')) > 1 else 'No additional details available.'}  

    **💡 Additional Notes:** AI-generated structured response for better clarity.
    """

    # Display AI Response **(only one per prompt)**
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_text = ""

        for word in formatted_response.split():
            response_text += word + " "
            time.sleep(0.04)  # Simulate typing effect
            response_placeholder.markdown(response_text)

    # Append AI Message (only one response per prompt)
    st.session_state.chat_sessions[st.session_state.current_chat]["messages"].append(AIMessage(content=formatted_response))
    st.session_state.chat_sessions[st.session_state.current_chat]["timestamps"].append(timestamp)

# Display Chat Messages (Only One AI Response per Prompt)
for msg, timestamp in zip(
    st.session_state.chat_sessions[st.session_state.current_chat]["messages"],
    st.session_state.chat_sessions[st.session_state.current_chat]["timestamps"]
):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
