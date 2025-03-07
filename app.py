import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai
import datetime
import os

# Set API Key
genai.configure(api_key="your_actual_api_key_here")

# Initialize Chat Model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# Streamlit UI Setup
st.set_page_config(page_title="AI Data Science Tutor", layout="wide")
st.title("🤖 AI Data Science Tutor")
st.markdown("Ask me anything about **Data Science!** I support **multi-turn conversations.**")

# Sidebar - Memory Settings
st.sidebar.header("⚙️ Chat Settings")
memory_enabled = st.sidebar.checkbox("Enable Memory", value=True)

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.timestamps = []
    if os.path.exists("chat_history.txt"):
        os.remove("chat_history.txt")
    st.success("Chat history cleared!")

# Initialize Memory if Enabled
if memory_enabled:
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
else:
    memory = None  # No memory when disabled

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.timestamps = []  # Store timestamps

# Function to check if the question is related to Data Science
def is_data_science_question(question):
    keywords = ["data science", "machine learning", "AI", "deep learning", "statistics", 
                "Python", "NumPy", "Pandas", "Matplotlib", "scikit-learn", "neural networks",
                "clustering", "regression", "classification", "time series", "data preprocessing"]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in keywords)

# Function to save chat history to a file
def save_chat_history():
    with open("chat_history.txt", "w") as file:
        for msg, timestamp in zip(st.session_state.messages, st.session_state.timestamps):
            role = "User" if isinstance(msg, HumanMessage) else "AI Tutor"
            file.write(f"[{timestamp}] {role}: {msg.content}\n")

# User Input
user_input = st.chat_input("Ask me a Data Science question...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append User Message & Timestamp (User message always on top)
    st.session_state.messages.insert(0, HumanMessage(content=user_input))
    st.session_state.timestamps.insert(0, timestamp)

    # Check if the question is related to Data Science
    if not is_data_science_question(user_input):
        response_text = "I'm here to assist with Data Science topics only. Please ask a Data Science-related question."
    else:
        # Retrieve Chat History from Memory
        chat_history = memory.load_memory_variables({})["chat_history"] if memory_enabled else []

        # Generate AI Response
        response = chat_model.predict_messages(chat_history + [HumanMessage(content=user_input)])
        response_text = response.content

    # Append AI Response & Timestamp (Directly below user message)
    response_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.insert(1, AIMessage(content=response_text))
    st.session_state.timestamps.insert(1, response_timestamp)

    # Save to Memory if Enabled
    if memory_enabled:
        memory.save_context({"input": user_input}, {"output": response_text})

    # Save chat history to file
    save_chat_history()

# Display Chat History (User Messages First)
for msg, timestamp in zip(st.session_state.messages, st.session_state.timestamps):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
