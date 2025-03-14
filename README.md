# AI Data Science Tutor Chatbot  

This is a **Streamlit-based AI chatbot** that leverages **Google Gemini API** to provide intelligent responses to data science-related queries. The chatbot supports **multi-chat sessions**, **AI summarization**, **PDF export**, **dark mode**, **IP banning**, and more.

---

## 🚀 **Features**  
✅ **Multi-Chat Support** – Users can create and switch between multiple chat sessions.  
✅ **AI-Powered Responses** – Uses Google Gemini API for intelligent and context-aware responses.  
✅ **Delete Chat Option** – Easily remove old conversations from the chat history.  
✅ **Real-time Streaming** – Responses appear dynamically as they are generated.  
✅ **PDF Export** – Save chat conversations as PDF files.  
✅ **Dark Mode** – Enhanced UI experience for users.  
✅ **AI Summarization** – Summarizes chat history for quick reference.  
✅ **IP Banning System** – Prevents unauthorized access based on IP addresses.  

---

## 🛠 **Installation & Setup**  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/AbhishekKantharia/AIConversationalDataScienceTutor.git
cd AIConversationalDataScienceTutor
```

### **2️⃣ Install Dependencies**  
Ensure you have Python installed, then run:  
```bash
pip install -r requirements.txt
```

### **3️⃣ Set Up Environment Variables**  
Create a `.env` file in the root directory and add:  
```env
GOOGLE_API_KEY=your_google_gemini_api_key
ADMIN_PASSWORD=your_admin_password
```

### **4️⃣ Run the Application**  
```bash
streamlit run app.py
```

---

## 📂 **File Structure**  

```
📁 ai-ds-tutor
│── app.py               # Main Streamlit application
│── requirements.txt     # Required Python packages
│── chat_sessions.pkl    # Stored chat sessions (auto-generated)
│── banned_ips.pkl       # Banned IPs list (auto-generated)
│── .env                 # API keys and admin password
│── README.md            # Documentation
```

---

## 📜 **Usage**  

1️⃣ **Ask a Question** – Type a data science-related question in the chat input.  
2️⃣ **Multi-Chat Support** – Create and switch between multiple chat sessions in the sidebar.  
3️⃣ **Delete Chat** – Remove a conversation using the "🗑️ Delete Chat" button.  
4️⃣ **Enable Dark Mode** – Switch to dark mode for better readability.  
5️⃣ **Export Chat to PDF** – Save your chat for later reference.  

---

## 🔐 **Admin Features**  

### **IP Banning**  
- The app can ban users based on IP addresses.  
- Banned users will see a **"🚫 Your IP has been banned."** message.  

### **Chat Summarization**  
- AI can generate summaries for long conversations, making it easier to review.  

---

## 🔧 **Customization**  

### **Modify the UI**  
To customize colors and styling, edit the **CSS inside `app.py`**:  
```python
st.markdown(
    """
    <style>
    body { background-color: #121212; color: #e0e0e0; }
    .stSidebar { background-color: #181818; }
    </style>
    """,
    unsafe_allow_html=True
)
```

### **Adjust the AI Model**  
To use a different **Google Gemini AI model**, change this line in `app.py`:  
```python
LATEST_GEMINI_MODEL = "gemini-1.5-pro-latest"
```

---

## 📌 **To-Do / Future Improvements**  
🔹 Improve response streaming for faster replies.  
🔹 Add a **user authentication system** for chat history security.  
🔹 Support **file uploads** for AI-based code reviews.  
🔹 Enhance **PDF export** formatting for better readability.  

---

## 🏆 **Contributing**  
Contributions are welcome! Feel free to submit a pull request or open an issue.  

---

## 📜 **License**  
This project is licensed under the **MIT License**.  

---

🎉 **Enjoy your AI-powered Data Science Chatbot!** 🚀
