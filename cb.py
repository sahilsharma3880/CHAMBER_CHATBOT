import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from db import MYSQL_Connection
from dotenv import load_dotenv

load_dotenv()

# Initialize DB (SQLite)
db = MYSQL_Connection()

# Page Config
st.set_page_config(
    page_title="CHAMBER",
    page_icon="🤖",
    layout="centered"
)

# Session State Setup
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "chat" not in st.session_state:
    st.session_state.chat = []

# LOGIN PAGE
if not st.session_state.logged_in:
    st.title("🔐 Login / Register")

    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = db.login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register"):
            if db.register_user(new_user, new_pass):
                st.success("Registered successfully! Please login.")
            else:
                st.error("Username already exists")

    with tab3:
        forgot_user = st.text_input("Enter Username")
        new_pass = st.text_input("Enter New Password", type="password")

        if st.button("Reset Password"):
            if db.reset_password(forgot_user, new_pass):
                st.success("Password Updated Successfully")
            else:
                st.error("Username Not Exists")

    st.stop()

# MAIN CHAT
st.title("🤖 CHAMBER")
st.caption("Your chats are saved securely")

# Sidebar
if st.sidebar.button("Clear Chat"):
    db.clear_chat(st.session_state.user_id)
    st.session_state.chat = []
    st.rerun()

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# Load Model (Using Streamlit Secrets)
model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    max_tokens=1000,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Load History
if not st.session_state.chat:
    st.session_state.chat = [
        SystemMessage(content="You are a friendly and helpful AI assistant.")
    ]

    history = db.fetch_history(st.session_state.user_id)
    for role, msg in reversed(history):
        if role == "user":
            st.session_state.chat.append(HumanMessage(content=msg))
        else:
            st.session_state.chat.append(AIMessage(content=msg))

# Display Chat
for message in st.session_state.chat:
    if isinstance(message, HumanMessage):
        st.chat_message("user").write(message.content)
    elif isinstance(message, AIMessage):
        st.chat_message("assistant").write(message.content)

# User Input
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)
    db.insert_message(st.session_state.user_id, "user", user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            response = model.invoke(st.session_state.chat)
            st.write(response.content)

    st.session_state.chat.append(AIMessage(content=response.content))
    db.insert_message(st.session_state.user_id, "assistant", response.content)


