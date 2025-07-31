import os
import re
import time
import base64
import streamlit as st
from backend import (
    load_students, 
    validate_environment, 
    authenticate_student, 
    process_user_question
)

# Validate environment first
try:
    validate_environment()
except Exception as e:
    st.error(str(e))
    st.stop()

# Load student database
try:
    STUDENT_DB = load_students()
except Exception as e:
    st.error(str(e))
    st.stop()

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

# -----------------------------
# Identity: simple email sign-in
# -----------------------------
if "student_email" not in st.session_state:
    with st.form("email_form"):
        email_in = st.text_input("Enter your Cal Poly email to begin:")
        submitted = st.form_submit_button("Continue")
        if submitted and email_in:
            st.session_state.student_email = email_in.strip().lower()
    st.stop()

email = st.session_state.student_email
student, error = authenticate_student(email, STUDENT_DB)
if error:
    st.warning(error)
    with st.expander("Available test emails"):
        st.json(list(STUDENT_DB.keys()))
    if st.button("Use a different email"):
        del st.session_state["student_email"]
        st.rerun()
    st.stop()

st.caption(f"Signed in as: {email}")

# --- CSS: reset, centered header, chat, footer ---
st.markdown("""
<style>
  html, body, .stApp {
    height: 100%; margin: 0; padding: 0;
  }
  .appview-container .main {
    padding-top: 20px;
  }

  /* Centered Header */
  .header-container {
    width: 100%;
    max-width: 600px;
    margin: 0 auto 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .header-container img {
    max-height: 60px;
    width: auto;
    margin-bottom: 0.5rem;
  }
  .header-container h1 {
    color: black;
    font-size: 2.5rem;
    margin: 0.25rem 0;
  }
  .header-container p {
    color: black;
    font-size: 1rem;
    margin: 0.25rem 0;
  }

  /* Chat Area */
  .chat-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 12px;
    max-height: 60vh;
    overflow-y: auto;
    margin-bottom: 80px;
  }
  .chat-message {
    max-width: 60%;
    padding: 10px 14px;
    border-radius: 16px;
    line-height: 1.4;
    word-wrap: break-word;
    overflow-wrap: break-word;
    margin: 4px 0;
  }
  .chat-message.user {
    background: #dcf8c6;
    margin-left: auto;
  }
  .chat-message.assistant {
    background: #f1f0f0;
    margin-right: auto;
  }

  /* Hide Streamlit's "Image not available" */
  .streamlit-expanderHeader .css-1t0sjvy img + div {
    display: none;
  }

  /* Sticky Footer */
  .footer {
    position: fixed;
    bottom: 0; left: 0; width: 100%;
    background-color: rgba(21,71,52,0.9);
    color: #DDDDDD;
    text-align: center;
    padding: 8px 0;
    font-size: 0.8rem;
    z-index: 1001;
  }
</style>
""", unsafe_allow_html=True)

# --- Header: logo, title, subtitle in one block ---
logo_path = "calpoly-logo.png"
logo_html = ""
if os.path.exists(logo_path):
    b64 = img_to_base64(logo_path)
    logo_html = f'<img src="data:image/png;base64,{b64}" alt="Cal Poly Logo" />'

header_html = f"""
<div class="header-container">
  {logo_html}
  <h1>MathPath AI</h1>
  <p>Your Personal Guide to Cal Poly's Math Placement System</p>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# --- Submission handler ---
def handle_submit():
    text = st.session_state.user_input.strip()
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.user_input = ""
    with st.spinner("Thinking..."):
        reply = process_user_question(student, text)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.typing = True

# Strip out any <Image> placeholders
def clean(text: str) -> str:
    return re.sub(r'<Image[^>]*\/>', '', text).strip()

# --- Chat display ---
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    msgs = st.session_state.messages

    if st.session_state.typing and msgs:
        # Render all but last
        for msg in msgs[:-1]:
            c = clean(msg["content"])
            if c:
                cls = "user" if msg["role"]=="user" else "assistant"
                st.markdown(f'<div class="chat-message {cls}">{c}</div>', unsafe_allow_html=True)

        # Typing effect on last message
        placeholder = st.empty()
        full_text = clean(msgs[-1]["content"])
        built = ""
        speed = 0.01
        for ch in full_text:
            built += ch
            placeholder.markdown(
                f'<div class="chat-message assistant">{built}</div>',
                unsafe_allow_html=True
            )
            time.sleep(speed)
        st.session_state.typing = False

    else:
        # Render all messages
        for msg in msgs:
            c = clean(msg["content"])
            if c:
                cls = "user" if msg["role"]=="user" else "assistant"
                st.markdown(f'<div class="chat-message {cls}">{c}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Input bar ---
st.text_input(
    label="Ask a question",
    key="user_input",
    placeholder="Type here…",
    on_change=handle_submit,
    label_visibility="hidden"
)

# --- Footer ---
st.markdown("""
<div class="footer">
  This chatbox is powered by AI for guidance and recommendations. Responses may contain errors, so always verify with an advisor.
</div>
""", unsafe_allow_html=True)
