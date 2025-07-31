import streamlit as st
import base64
from chatbot import query_bedrock

# Helper to load images as base64
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = img_to_base64("calpoly-logo.png")

# Page setup
st.set_page_config(page_title="MathPath AI", layout="centered")

# Global CSS (including footer fix)
st.markdown("""
<style>
  /* 1. Full-height reset */
  html, body, .stApp {
    height: 100%;
    margin: 0;
    padding: 0;
  }

  /* 2. Top padding for header */
  .appview-container .main {
    padding-top: 80px;
  }

  /* 3. Page title centered */
  .page-title {
    position: absolute;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60%;
    text-align: center;
    color: white;
    font-size: 2.5rem;
    font-weight: bold;
    z-index: 1001;
  }

  /* 4. Input bar styling */
  .input-bar {
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60%;
    z-index: 1001;
  }
  .input-bar input {
    width: 100% !important;
  }

  /* 5. Chat container with bottom margin to avoid overlap */
  .chat-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
    max-height: 60vh;
    overflow-y: auto;
    margin-bottom: 80px;  /* ensure space above the footer */
  }

  .chat-message {
    max-width: 60%;
    padding: 10px 14px;
    border-radius: 16px;
    line-height: 1.4;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }

  .chat-message.user {
    background-color: #dcf8c6;
    margin-left: auto;
  }

  .chat-message.assistant {
    background-color: #f1f0f0;
    margin-right: auto;
  }

  /* 6. Sticky footer */
  .footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 8px 0;
    background-color: rgba(21, 71, 52, 0.9);
    text-align: center;
    color: #DDDDDD;
    font-size: 0.8rem;
    z-index: 1001;
  }

  /* 7. Background color */
  body, .stApp {
    background-color: #154734 !important;
  }
</style>
""", unsafe_allow_html=True)

# Logo banner
st.markdown(f"""
<div class="banner">
  <img src="data:image/png;base64,{logo_b64}" alt="Logo">
</div>
""", unsafe_allow_html=True)

# Page title
st.markdown('<div class="page-title">MathPath AI</div>', unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handler for new messages
def handle_submit():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.user_input = ""
    with st.spinner("Thinking..."):
        reply = query_bedrock(user_input)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Display chat
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        cls = "user" if msg["role"] == "user" else "assistant"
        st.markdown(f'<div class="chat-message {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input bar
with st.container():
    st.markdown('<div class="input-bar">', unsafe_allow_html=True)
    st.text_input(
        label="Ask a question",
        key="user_input",
        placeholder="Type here…",
        on_change=handle_submit,
        label_visibility="hidden"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Sticky footer (placed last)
st.markdown("""
<div class="footer">
  This chatbox is powered by AI for guidance and recommendations. Responses may contain errors, so always verify with an advisor.
</div>
""", unsafe_allow_html=True)
