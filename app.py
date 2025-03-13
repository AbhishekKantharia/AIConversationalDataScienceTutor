# Ensure chat_sessions is initialized
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Ensure current_chat is initialized
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# Multi-Chat Support (if enabled)
if st.session_state.multi_chat:
    st.sidebar.header("📂 Chat Sessions")

    if st.sidebar.button("➕ New Chat"):
        new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_chat_id] = {"messages": [], "timestamps": []}
        st.session_state.current_chat = new_chat_id

    chat_names = list(st.session_state.chat_sessions.keys())
    if chat_names:
        selected_chat = st.sidebar.radio("💬 Select a Chat", chat_names)
        st.session_state.current_chat = selected_chat

    if st.session_state.current_chat is None and chat_names:
        st.session_state.current_chat = chat_names[0]

    # 🗑️ Delete Chat Button
    if st.session_state.current_chat:
        if st.sidebar.button("🗑️ Delete Chat"):
            del st.session_state.chat_sessions[st.session_state.current_chat]
            chat_names = list(st.session_state.chat_sessions.keys())  # Refresh chat list
            st.session_state.current_chat = chat_names[0] if chat_names else None
            st.experimental_rerun()  # Refresh UI
