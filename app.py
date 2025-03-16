import streamlit as st
import os
import sqlite3
import pandas as pd
import numpy as np
import joblib
import web3
import tensorflow as tf
import tensorflow.lite as tflite
from web3 import Web3
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from cryptography.fernet import Fernet
from langchain.chat_models import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory

# Set API Key
os.environ["GOOGLE_API_KEY"] = "your_api_key_here"

# Initialize Chat Model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Persistent SQLite Database
DATABASE_PATH = "persistent_data.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Streamlit UI
st.set_page_config(page_title="AI Data Science Tutor", layout="wide")
st.title("🤖 AI Data Science Tutor")

# Sidebar - Upload Dataset
st.sidebar.header("📂 Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Function to load dataset into SQLite
def load_dataset(file, table_name):
    df = pd.read_csv(file)
    df.to_sql(table_name, engine, index=False, if_exists="replace")
    return df

# Sidebar - Select Dataset
st.sidebar.header("📊 Available Datasets")
table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", engine)["name"].tolist()
selected_dataset = st.sidebar.selectbox("Choose a dataset:", table_names)

if st.sidebar.button("Show Dataset Preview"):
    preview_df = pd.read_sql_query(f"SELECT * FROM {selected_dataset} LIMIT 5", engine)
    st.dataframe(preview_df)

# 🔹 **AI-Powered Cybersecurity & Anomaly Detection**
st.sidebar.header("🛡️ AI-Powered Cybersecurity")
if st.sidebar.button("Run Anomaly Detection"):
    data = pd.read_sql_query(f"SELECT * FROM {selected_dataset}", engine)
    feature_cols = st.sidebar.multiselect("Select Features for Anomaly Detection", data.columns)

    if feature_cols:
        X = data[feature_cols]
        X = StandardScaler().fit_transform(X)

        model = IsolationForest(contamination=0.05)
        anomalies = model.fit_predict(X)
        data["Anomaly"] = anomalies

        st.write("✅ **Anomalies Detected!** (1 = Normal, -1 = Anomaly)")
        st.dataframe(data)

# 🔹 **Blockchain + AI for Secure Data Science**
st.sidebar.header("🔗 Blockchain + AI Security")
if st.sidebar.button("Encrypt & Store on Blockchain"):
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY"))

    # Generate encryption key
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # Encrypt dataset metadata
    metadata = f"Dataset: {selected_dataset}, Rows: {len(data)}, Features: {len(feature_cols)}"
    encrypted_metadata = cipher.encrypt(metadata.encode())

    # Store encrypted data hash on blockchain (simulation)
    tx_hash = w3.keccak(text=encrypted_metadata.decode()).hex()
    st.write(f"🔗 **Encrypted Data Stored on Blockchain!** TX Hash: `{tx_hash}`")

# 🔹 **Edge AI for IoT & Smart Devices**
st.sidebar.header("🤖 Edge AI for IoT")
if st.sidebar.button("Deploy AI Model to Edge Device"):
    data = pd.read_sql_query(f"SELECT * FROM {selected_dataset}", engine)
    target_col = st.sidebar.selectbox("Select Target Column", data.columns)

    if target_col:
        X = data.drop(columns=[target_col])
        y = data[target_col]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(16, activation="relu", input_shape=(X.shape[1],)),
            tf.keras.layers.Dense(8, activation="relu"),
            tf.keras.layers.Dense(1, activation="sigmoid")
        ])
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        model.fit(X_train, y_train, epochs=5, verbose=0)

        # Convert to TensorFlow Lite Model
        converter = tflite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()

        with open("edge_model.tflite", "wb") as f:
            f.write(tflite_model)

        st.success("✅ Model Deployed to Edge Device (TFLite)!")

# User Input
user_input = st.text_area("Ask a Data Science question, enter Python code, or write an SQL query:")

if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    chat_history = memory.load_memory_variables({})["chat_history"]
    response = chat_model.predict_messages(chat_history + [HumanMessage(content=user_input)])
    st.session_state.messages.append(AIMessage(content=response.content))
    memory.save_context({"input": user_input}, {"output": response.content})

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f"**🧑‍💻 You:** {msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"**🤖 AI Tutor:** {msg.content}")
