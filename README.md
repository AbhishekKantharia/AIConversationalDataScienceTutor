### **📜 README.md**  

# 🚀 ChatGPT-Style AI Data Science Tutor  
### Powered by Google Gemini 1.5 Pro | Multi-User Authentication | Secure & Free  

## 🌟 Features  
✅ **Google Gemini 1.5 Pro** – Latest AI model with **real-time responses**  
✅ **ChatGPT-Style UI** – Interactive multi-chat system, rename/delete chats  
✅ **Multi-User Authentication** – Secure login with **Admin & User roles**  
✅ **Role-Based Access Control** – Admins can **unblock banned IPs**  
✅ **IP Banning for Security** – Auto-blocks **suspicious activity**  
✅ **Persistent Chat History** – Saves & restores chats seamlessly  
✅ **100% Free & No Paywalls** – Premium AI services at **zero cost**  

---

## 📥 Installation  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/yourusername/aiconversationaldatasciencetutor.git
cd aiconversationaldatasciencetutor
```

### **2️⃣ Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **3️⃣ Set Up Environment Variables**  
Create a `.env` file in the root directory and add:  
```
ADMIN_PASSWORD=your_admin_password
USER_PASSWORD=your_user_password
SECRET_KEY=your_secret_key
```

### **4️⃣ Run the Application**  
```bash
streamlit run app.py
```

---

## 🛠 Requirements  
This project requires **Python 3.8+** and the following dependencies:  
```plaintext
streamlit
langchain
langchain_google_genai
google-generativeai
requests
python-dotenv
bcrypt
streamlit-authenticator
```
To install all dependencies:  
```bash
pip install -r requirements.txt
```

---

## 🎯 Usage  

### **🔑 User Authentication**  
- **Users**: Can chat with AI but cannot unblock IPs  
- **Admins**: Have extra privileges (e.g., **unblocking banned users**)  

### **💬 ChatGPT-Style Conversations**  
- **Real-time responses** with **streaming output**  
- **Multi-chat support** – create, rename, delete, and switch chats  

### **🔒 Security**  
- **Auto IP Ban** – Detects & blocks malicious activities  
- **Admin Dashboard** – Unblock users securely  

---

## 🔐 Admin Controls  

### **1️⃣ Unblock an IP**  
Admins can **unblock users** from the **sidebar settings**.  
1. Log in as **Admin**  
2. Enter the **banned IP address**  
3. Click **Unblock** ✅  

---

## 📌 Future Enhancements  
🔹 **User Registration System** – Allow users to sign up dynamically  
🔹 **Database Integration** – Store chats & user credentials securely  
🔹 **Analytics Dashboard** – Monitor chat activity & security logs  

---

## 🤝 Contributing  
Want to **improve** this project? 🎉 Feel free to fork, clone, and **submit pull requests**!  

---

## 📄 License  
This project is licensed under the **MIT License** – use it freely!  

---

## 💬 Need Help?  
For issues, feel free to create a [GitHub Issue](https://github.com/yourusername/aiconversationaldatasciencetutor/issues).  

🌟 **Star this repo** if you found it useful! ⭐  

---

### **✨ Why This README is Great?**  
✅ **Clear Installation Steps**  
✅ **Secure Password Management with `.env`**  
✅ **Detailed Feature List**  
✅ **Role-Based Access Documentation**  
✅ **Future Enhancements Section**  

Would you like **database integration** for user authentication next? 🚀😊
