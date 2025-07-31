import streamlit as st
import base64
import time
from chatbot import query_bedrock

# Helper to load images as base64
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = img_to_base64("calpoly-logo.png")

# Page setup
st.set_page_config(page_title="MathPath AI", layout="centered")

# Initialize session‐state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "typing" not in st.session_state:
    st.session_state.typing = False

# CSS (including sticky footer)
st.markdown("""
<style>
  html, body, .stApp { height: 100%; margin: 0; padding: 0; }
  .appview-container .main { padding-top: 80px; }
  .page-title {
    position: absolute; top: 40%; left: 50%;
    transform: translate(-50%, -50%);
    width: 60%; text-align: center;
    color: white; font-size: 2.5rem; font-weight: bold;
    z-index: 1001;
  }
  .input-bar {
    position: absolute; top: 55%; left: 50%;
    transform: translate(-50%, -50%);
    width: 60%; z-index: 1001;
  }
  .input-bar input { width: 100% !important; }
  .chat-container {
    display: flex; flex-direction: column;
    gap: 12px; padding: 12px;
    max-height: 60vh; overflow-y: auto;
    margin-bottom: 80px;
  }
  .chat-message {
    max-width: 60%; padding: 10px 14px;
    border-radius: 16px; line-height: 1.4;
    word-wrap: break-word; overflow-wrap: break-word;
  }
  .chat-message.user { background-color: #dcf8c6; margin-left: auto; }
  .chat-message.assistant { background-color: #f1f0f0; margin-right: auto; }
  .footer {
    position: fixed; bottom: 0; left: 0;
    width: 100%; padding: 8px 0;
    background-color: rgba(21,71,52,0.9);
    text-align: center; color: #DDDDDD;
    font-size: 0.8rem; z-index: 1001;
  }
  body, .stApp { background-color: #154734 !important; }
</style>
""", unsafe_allow_html=True)

# Logo
st.markdown(f"""
<div class="banner">
  <img src="data:image/png;base64,{logo_b64}" alt="Logo">
</div>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="page-title">MathPath AI</div>', unsafe_allow_html=True)

# Submission handler
def handle_submit():
    text = st.session_state.user_input.strip()
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.user_input = ""
    with st.spinner("Thinking..."):
        reply = query_bedrock(text)
    # Queue the assistant reply but defer its render
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.typing = True

# Chat display
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    msgs = st.session_state.messages

    if st.session_state.typing and msgs:
        # Render all but last assistant message
        for msg in msgs[:-1]:
            cls = "user" if msg["role"] == "user" else "assistant"
            st.markdown(f'<div class="chat-message {cls}">{msg["content"]}</div>', unsafe_allow_html=True)

        # Typing placeholder
        placeholder = st.empty()
        full_text = msgs[-1]["content"]
        rendered = ""

        for ch in full_text:
            rendered += ch
            placeholder.markdown(f'<div class="chat-message assistant">{rendered}</div>', unsafe_allow_html=True)
            time.sleep(0.03)

        # Turn off typing flag so next rerun shows normal
        st.session_state.typing = False

    else:
        # No typing in progress: render all messages normally
        for msg in msgs:
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

# Sticky footer
st.markdown("""
<div class="footer">
  This chatbox is powered by AI for guidance and recommendations. Responses may contain errors, so always verify with an advisor.
</div>
""", unsafe_allow_html=True)
