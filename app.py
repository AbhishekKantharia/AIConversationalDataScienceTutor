import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai

# Set API Key (Alternatively, use env variables)

genai.configure(api_key="your_actual_api_key_here")

try:
    response = genai.GenerativeModel("gemini-pro").generate_content("Hello!")
    print(response.text)
except Exception as e:
    print("Error:", e)

# Initialize Chat Model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# Initialize Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Streamlit UI
st.set_page_config(page_title="AI Data Science Tutor", layout="wide")
st.title("🤖 AI Data Science Tutor")

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are an AI tutor specialized in Data Science. Answer only Data Science-related questions.")
    ]

# User Input
user_input = st.text_input("Ask me a Data Science question:")

if user_input:
    # Append User Message
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Retrieve Chat History from Memory
    chat_history = memory.load_memory_variables({})["chat_history"]

    # Generate AI Response
    response = chat_model.predict_messages(chat_history + [HumanMessage(content=user_input)])

    # Append AI Response to Chat
    st.session_state.messages.append(AIMessage(content=response.content))

    # Save to Memory
    memory.save_context({"input": user_input}, {"output": response.content})

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f"**🧑‍💻 You:** {msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"**🤖 AI Tutor:** {msg.content}")
