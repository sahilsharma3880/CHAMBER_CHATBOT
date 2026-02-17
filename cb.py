import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from db import MYSQL_Connection

load_dotenv()

db = MYSQL_Connection(
    host="localhost",
    user="root",
    password="Sahil@3880",
    database="chatbot_results"
)

db.create_db_and_table()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "chat" not in st.session_state:
    st.session_state.chat = []

st.set_page_config(
    page_title="CHATBOT",
    page_icon="🤖",
    layout="centered"
)

if not st.session_state.logged_in:
    st.title("🔐 Login / Register")

    tab1, tab2 , tab3 = st.tabs(["Login", "Register" , "Forgot Password"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password" ,key = "login pass")

        if st.button("Login"):
            user = db.login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.success("Login successful ")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password" , key = "reg pass")

        if st.button("Register"):
            if db.register_user(new_user, new_pass):
                st.success("Registered successfully! Please login.")
            else:
                st.error("Username already exists")

    with tab3:
        forgot_user = st.text_input("Enter Username" , key = "forgot user")
        new_pass = st.text_input("Enter New Password" , type = "password" , key = "forgot pass")

        if st.button("Reset Password"):
            if db.reset_password(forgot_user , new_pass):
                st.success("Password Updated Succesfully")
            else:
                st.error("Username Not Exists")

    st.stop()

st.title("🤖 CHAMBER")
st.caption("Your chats are saved securely")

st.sidebar.title("Controls")

if st.sidebar.button("Clear Chat"):
    db.clear_chat(st.session_state.user_id)
    st.session_state.chat = [
        SystemMessage(content="You are a friendly, helpful AI assistant."),
        AIMessage(content="Chat cleared! Ask me something new 😄")
    ]
    st.rerun()

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    max_tokens=1000
)

#LOAD CHAT
if not st.session_state.chat:
    st.session_state.chat = [
        SystemMessage(
            content="""You are a friendly, helpful AI assistant.
            Explain concepts clearly and use examples so that user top the exams💀💀💀."""
        )
    ]

    history = db.fetch_history(st.session_state.user_id)
    for role, msg in reversed(history):
        if role == "user":
            st.session_state.chat.append(HumanMessage(content=msg))
        else:
            st.session_state.chat.append(AIMessage(content=msg))

# DISPLAY CHAT
for message in st.session_state.chat:
    if isinstance(message, HumanMessage):
        st.chat_message("user", avatar=r"D:\llm\working.png").write(message.content)
    elif isinstance(message, AIMessage):
        st.chat_message("assistant", avatar=r"D:\llm\chatbot.png").write(message.content)

# USER INPUT
user_input = st.chat_input("Type your message...")

if user_input:
    # User message
    st.session_state.chat.append(HumanMessage(content=user_input))
    st.chat_message("user", avatar=r"D:\llm\working.png").write(user_input)
    db.insert_message(st.session_state.user_id, "user", user_input)

    # AI response
    with st.chat_message("assistant", avatar=r"D:\llm\chatbot.png"):
        with st.spinner("Thinking... 🤔"):
            response = model.invoke(st.session_state.chat)
            st.write(response.content)

    st.session_state.chat.append(AIMessage(content=response.content))
    db.insert_message(st.session_state.user_id, "assistant", response.content)
