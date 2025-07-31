import os
import re
import time
import base64
import streamlit as st
from chatbot import query_bedrock

# Helper to load images as base64
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Page setup
st.set_page_config(page_title="MathPath AI", layout="centered")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "typing" not in st.session_state:
    st.session_state.typing = False

# CSS (chat bubbles, hide placeholder, sticky footer)
st.markdown("""
<style>
  html, body, .stApp { height:100%; margin:0; padding:0; }
  .appview-container .main { padding-top:80px; }

  .chat-container {
    display:flex; flex-direction:column;
    gap:20px;
    padding:12px;
    max-height:60vh; overflow-y:auto;
    margin-bottom:80px;
  }
  .chat-message {
    max-width:60%; padding:10px 14px;
    border-radius:16px; line-height:1.4;
    word-wrap:break-word; overflow-wrap:break-word;
    margin:4px 0;
  }
  .chat-message.user      { background:#dcf8c6; margin-left:auto; }
  .chat-message.assistant { background:#f1f0f0; margin-right:auto; }

  /* Hide Streamlit's "Image not available" placeholder */
  .streamlit-expanderHeader .css-1t0sjvy img + div {
    display: none;
  }

  /* Sticky footer */
  .footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: rgba(21,71,52,0.9);
    color: #DDDDDD;
    text-align: center;
    padding: 8px 0;
    font-size: 0.8rem;
    z-index: 1001;
  }
</style>
""", unsafe_allow_html=True)

# Logo banner (only if file exists)
logo_path = "calpoly-logo.png"
if os.path.exists(logo_path):
    logo_b64 = img_to_base64(logo_path)
    st.markdown(f'''
    <div style="text-align:center; margin-bottom:1rem;">
      <img src="data:image/png;base64,{logo_b64}" style="max-height:60px;" />
    </div>
    ''', unsafe_allow_html=True)

# Submission handler
def handle_submit():
    text = st.session_state.user_input.strip()
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.user_input = ""
    with st.spinner("Thinking..."):
        reply = query_bedrock(text)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.typing = True

# Function to remove inlined <Image> placeholders
def clean(msg: str) -> str:
    return re.sub(r'<Image[^>]*\/>', '', msg).strip()

# Chat display
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    msgs = st.session_state.messages

    if st.session_state.typing and msgs:
        # Render existing messages except last
        for msg in msgs[:-1]:
            content = clean(msg["content"])
            if content:
                cls = "user" if msg["role"]=="user" else "assistant"
                st.markdown(f'<div class="chat-message {cls}">{content}</div>',
                            unsafe_allow_html=True)

        # Typing effect for the last assistant message
        placeholder = st.empty()
        full_text = clean(msgs[-1]["content"])
        rendered = ""
        typing_speed = 0.01  # seconds per character

        for ch in full_text:
            rendered += ch
            placeholder.markdown(
                f'<div class="chat-message assistant">{rendered}</div>',
                unsafe_allow_html=True
            )
            time.sleep(typing_speed)
        st.session_state.typing = False

    else:
        # Render all messages without typing effect
        for msg in msgs:
            content = clean(msg["content"])
            if content:
                cls = "user" if msg["role"]=="user" else "assistant"
                st.markdown(f'<div class="chat-message {cls}">{content}</div>',
                            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Input bar
st.text_input(
    label="Ask a question",
    key="user_input",
    placeholder="Type here…",
    on_change=handle_submit,
    label_visibility="hidden"
)

# Sticky footer
st.markdown("""
<div class="footer">
  This chatbox is powered by AI for guidance and recommendations. Responses may contain errors, so always verify with an advisor.
</div>
""", unsafe_allow_html=True)
