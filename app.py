import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai
import datetime
import os
import speech_recognition as sr
from fpdf import FPDF
import nbformat

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

# Function to save chat history as a PDF
def save_chat_as_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, "AI Data Science Tutor - Chat History", ln=True, align="C")
    pdf.ln(10)
    
    for msg, timestamp in zip(st.session_state.messages, st.session_state.timestamps):
        role = "User" if isinstance(msg, HumanMessage) else "AI Tutor"
        pdf.multi_cell(0, 10, f"[{timestamp}] {role}: {msg.content}\n")
        pdf.ln(2)

    pdf_file_path = "chat_history.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Function to save chat as a Jupyter Notebook
def save_chat_as_notebook():
    nb = nbformat.v4.new_notebook()
    cells = []
    
    for msg, timestamp in zip(st.session_state.messages, st.session_state.timestamps):
        role = "User" if isinstance(msg, HumanMessage) else "AI Tutor"
        text = f"**[{timestamp}] {role}:** {msg.content}"
        cells.append(nbformat.v4.new_markdown_cell(text))

    nb.cells = cells
    nb_file_path = "chat_history.ipynb"
    
    with open(nb_file_path, "w") as f:
        nbformat.write(nb, f)
    
    return nb_file_path

# Function to capture voice input
def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now!")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("😕 Sorry, could not understand the audio.")
    except sr.RequestError:
        st.error("⚠️ Could not request results, check your internet connection.")
    return None

# Sidebar - Download Chat History
st.sidebar.header("📄 Download Chat History")
if st.sidebar.button("📥 Download as PDF"):
    pdf_path = save_chat_as_pdf()
    with open(pdf_path, "rb") as file:
        st.sidebar.download_button("Download PDF", file, file_name="chat_history.pdf")

if st.sidebar.button("📓 Download as Jupyter Notebook"):
    notebook_path = save_chat_as_notebook()
    with open(notebook_path, "rb") as file:
        st.sidebar.download_button("Download Notebook", file, file_name="chat_history.ipynb")

# User Input (with voice support)
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.chat_input("Ask me a Data Science question...")

with col2:
    if st.button("🎙️ Speak"):
        spoken_text = voice_to_text()
        if spoken_text:
            user_input = spoken_text
            st.success(f"🗣️ You said: {spoken_text}")

if user_input:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append User Message & Timestamp (User message always on top)
    st.session_state.messages.insert(0, HumanMessage(content=user_input))
    st.session_state.timestamps.insert(0, timestamp)

    # Retrieve Chat History from Memory
    chat_history = memory.load_memory_variables({})["chat_history"] if memory_enabled else []

    # Generate AI Response
    response = chat_model.predict_messages(chat_history + [HumanMessage(content=user_input)])

    # Append AI Response & Timestamp (Directly below user message)
    response_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.insert(1, AIMessage(content=response.content))
    st.session_state.timestamps.insert(1, response_timestamp)

    # Save to Memory if Enabled
    if memory_enabled:
        memory.save_context({"input": user_input}, {"output": response.content})

# Display Chat History (User Messages First)
for msg, timestamp in zip(st.session_state.messages, st.session_state.timestamps):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(f"**[{timestamp}]** {msg.content}")
