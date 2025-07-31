# app.py

import os
import re
import time
import base64
import streamlit as st

from backend import (
    load_students,
    validate_environment,
    authenticate_student,
    process_user_question,
)

# -----------------------------------------------------------------------------
# 1) Page config
# -----------------------------------------------------------------------------
st.set_page_config(page_title="MathPath AI", layout="centered")

# -----------------------------------------------------------------------------
# 2) Helper: inline-embed PNGs as Base64
# -----------------------------------------------------------------------------
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# -----------------------------------------------------------------------------
# 3) Validate environment and load student DB
# -----------------------------------------------------------------------------
try:
    validate_environment()
    STUDENT_DB = load_students()
except Exception as e:
    st.error(str(e))
    st.stop()

# -----------------------------------------------------------------------------
# 4) Initialize session state
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "typing" not in st.session_state:
    st.session_state.typing = False

# -----------------------------------------------------------------------------
# 5) Email sign-in form
# -----------------------------------------------------------------------------
if "student_email" not in st.session_state:
    with st.form("email_form"):
        email_in = st.text_input("Enter your Cal Poly email to begin:")
        submitted = st.form_submit_button("Continue")
        if submitted and email_in:
            st.session_state.student_email = email_in.strip().lower()
            st.stop()
    st.stop()

# -----------------------------------------------------------------------------
# 6) Authenticate student
# -----------------------------------------------------------------------------
email = st.session_state.student_email
student, error = authenticate_student(email, STUDENT_DB)
if error:
    st.warning(error)
    with st.expander("Available test emails"):
        st.json(list(STUDENT_DB.keys()))
    if st.button("Use a different email"):
        del st.session_state["student_email"]
        st.stop()
    st.stop()

# Pull the student’s first and last name
first = student["person"].get("first_name", "")
last  = student["person"].get("last_name", "")

# Build logo HTML for the top banner only
logo_path = "calpoly-logo.png"
logo_html = ""
if os.path.exists(logo_path):
    b64 = img_to_base64(logo_path)
    logo_html = f'<img src="data:image/png;base64,{b64}" alt="Cal Poly Logo" />'

# -----------------------------------------------------------------------------
# 7) Inject CSS for the fixed banner + page padding
# -----------------------------------------------------------------------------
st.markdown("""
<style>
  /* Push app content below the banner */
  div[data-testid="stAppViewContainer"] {
    padding-top: 80px !important;
  }

  /* Fixed top banner */
  .banner {
    position: fixed;
    top: 0; left: 0; right: 0;
    background-color: #154734;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 20px;
    z-index: 9999;
    box-sizing: border-box;
  }
  .banner img {
    height: 40px;
    width: auto;
  }
  .banner .user-name {
    color: #ffffff;
    font-size: 1.2rem;
    font-weight: 500;
  }

  /* Centered header styling (no image) */
  .header-container {
    width: 100%;
    max-width: 600px;
    margin: 1.5rem auto;
    text-align: center;
  }
  .header-container h1 {
    color: #000;
    font-size: 2.5rem;
    margin: 0.25rem 0;
  }
  .header-container p {
    color: #000;
    font-size: 1rem;
    margin: 0.25rem 0;
  }

  /* Chat area styling */
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
    background: #8EAB9D;
    margin-left: auto;
  }
  .chat-message.assistant {
    background: #f1f0f0;
    margin-right: auto;
  }

  /* Sticky footer */
  .footer {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background-color: rgba(21,71,52,0.9);
    color: #DDD;
    text-align: center;
    padding: 8px 0;
    font-size: 0.8rem;
    z-index: 1001;
  }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8) Render the fixed banner (logo on left, name on right)
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="banner">
  {logo_html}
  <div class="user-name">{first} {last}</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9) Header (no image) + Chat UI + Footer
# -----------------------------------------------------------------------------
header_html = """
<div class="header-container">
  <h1>MathPath AI</h1>
  <p>Your Personal Guide to Cal Poly's Math Placement System</p>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

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

def clean(text: str) -> str:
    return re.sub(r'<Image[^>]*\/>', '', text).strip()

with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    msgs = st.session_state.messages

    if st.session_state.typing and msgs:
        for msg in msgs[:-1]:
            c = clean(msg["content"])
            if c:
                cls = "user" if msg["role"] == "user" else "assistant"
                st.markdown(f'<div class="chat-message {cls}">{c}</div>', unsafe_allow_html=True)

        placeholder = st.empty()
        full_text = clean(msgs[-1]["content"])
        built = ""
        for ch in full_text:
            built += ch
            placeholder.markdown(
                f'<div class="chat-message assistant">{built}</div>',
                unsafe_allow_html=True
            )
            time.sleep(0.01)
        st.session_state.typing = False

    else:
        for msg in msgs:
            c = clean(msg["content"])
            if c:
                cls = "user" if msg["role"] == "user" else "assistant"
                st.markdown(f'<div class="chat-message {cls}">{c}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.text_input(
    label="Ask a question",
    key="user_input",
    placeholder="Type here…",
    on_change=handle_submit,
    label_visibility="hidden"
)

st.markdown("""
<div class="footer">
  This chatbox is powered by AI for guidance and recommendations. Responses may contain errors, so always verify with an advisor.
</div>
""", unsafe_allow_html=True)
