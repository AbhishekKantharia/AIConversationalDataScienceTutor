import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai

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

# Initialize Memory if Enabled
if memory_enabled:
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
else:
    memory = None  # No memory when disabled

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are an AI tutor specialized in Data Science. Answer only Data Science-related questions.")
    ]

# User Input
user_input = st.chat_input("Ask me a Data Science question...")

if user_input:
    # Append User Message
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Retrieve Chat History from Memory
    chat_history = memory.load_memory_variables({})["chat_history"] if memory_enabled else []

    # Generate AI Response
    response = chat_model.predict_messages(chat_history + [HumanMessage(content=user_input)])

    # Append AI Response to Chat
    st.session_state.messages.append(AIMessage(content=response.content))

    # Save to Memory if Enabled
    if memory_enabled:
        memory.save_context({"input": user_input}, {"output": response.content})

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(f"**🧑‍💻 You:** {msg.content}")
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(f"**🤖 AI Tutor:** {msg.content}")
