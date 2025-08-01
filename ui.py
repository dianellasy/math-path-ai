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
# 2) CSS tweaks: banner, chat, header, footer + input styling
# -----------------------------------------------------------------------------
st.markdown("""
<style>
  /* push content below fixed banner */
  div[data-testid="stAppViewContainer"] { padding-top: 80px !important; }

  /* fixed top banner */
  .banner {
    position: fixed; top: 0; left: 0; right: 0;
    background-color: #154734;
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 20px; z-index: 9999;
  }
  .banner img { height: 40px; }
  .banner .user-name { color: #fff; font-size: 1.2rem; font-weight: 500; }

  /* header */
  .header-container {
    max-width: 700px; margin: 1.5rem auto; text-align: center;
  }
  .header-container h1 { font-size: 3.5rem; margin: 0.25rem 0; }
  .header-container p { font-size: 1.5rem; margin: 0.25rem 0; }

  /* chat area */
  .chat-container {
    display: flex; flex-direction: column; gap: 24px;
    padding: 12px;
    max-height: calc(100vh - 80px /*banner*/ - 60px /*input*/ - 40px /*footer*/);
    overflow-y: auto; margin: 0 auto;
    max-width: 800px; width: 100%;
  }

  /* chat bubbles */
  .chat-message {
    font-size: 1.1rem; line-height: 1.6;
    padding: 12px 18px; border-radius: 16px;
    word-wrap: break-word; overflow-wrap: break-word;
    margin: 8px 0; max-width: 90%;
  }
  .chat-message.user { background: #A8CCBA; margin-left: auto; }
  .chat-message.assistant { background: #f1f0f0; margin-right: auto; }

  /* searching animation */
  @keyframes dots {
    0%,25%   { content: ""; }
    50%      { content: "."; }
    75%      { content: ".."; }
    100%     { content: "..."; }
  }
  .chat-message.searching {
    position: relative; font-style: italic; color: #555;
  }
  .chat-message.searching::before {
    content: "Searching for information";
  }
  .chat-message.searching::after {
    content: "";
    animation: dots 1s steps(4,end) infinite;
    margin-left: 4px;
  }

  /* input container pinned above footer */
  .input-container {
    position: fixed; bottom: 40px; left: 0; right: 0;
    max-width: 800px; margin: 0 auto; padding: 8px 12px;
    background-color: #fff; z-index: 1002;
  }
  .input-container .stTextInput>div>div>input {
    width: 100%; padding: 0.75rem 1rem;
    font-size: 1rem; border-radius: 8px; border: 1px solid #ccc;
  }

  /* sticky footer */
  .footer {
    position: fixed; bottom: 0; left: 0; right: 0;
    background-color: rgba(21,71,52,0.9);
    color: #DDD; text-align: center; padding: 8px 0;
    font-size: 0.8rem; z-index: 1001;
  }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3) Helper: embed PNGs as Base64 for the logo
# -----------------------------------------------------------------------------
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# -----------------------------------------------------------------------------
# 4) Load & validate
# -----------------------------------------------------------------------------
try:
    validate_environment()
    STUDENT_DB = load_students()
except Exception as e:
    st.error(str(e))
    st.stop()

# -----------------------------------------------------------------------------
# 5) Session‐state init
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_searching" not in st.session_state:
    st.session_state.show_searching = False
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

# -----------------------------------------------------------------------------
# 6) Prepare logo HTML
# -----------------------------------------------------------------------------
logo_html = ""
if os.path.exists("calpoly-logo.png"):
    b64 = img_to_base64("calpoly-logo.png")
    logo_html = f'<img src="data:image/png;base64,{b64}" alt="Cal Poly Logo" />'

# -----------------------------------------------------------------------------
# 7) Top banner (pre‐login)
# -----------------------------------------------------------------------------
st.markdown(f'<div class="banner">{logo_html}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8) Welcome flow
# -----------------------------------------------------------------------------
if "student_email" not in st.session_state:
    st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    if logo_html:
        st.markdown(logo_html, unsafe_allow_html=True)
    st.markdown('<h2>Welcome to MathPath AI</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p>Your personal guide through Cal Poly’s math placement process.</p>',
        unsafe_allow_html=True
    )
    with st.form("email_form"):
        email_in = st.text_input("", placeholder="you@calpoly.edu")
        if st.form_submit_button("Continue") and email_in:
            st.session_state.student_email = email_in.strip().lower()
            st.stop()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# 9) Authenticate student
# -----------------------------------------------------------------------------
email = st.session_state.student_email
student, error = authenticate_student(email, STUDENT_DB)
if error:
    st.warning(error)
    with st.expander("Available test emails"):
        st.json(list(STUDENT_DB.keys()))
    if st.button("Use a different email"):
        del st.session_state.student_email
        st.stop()
    st.stop()

first = student["person"].get("first_name", "")
last  = student["person"].get("last_name", "")

# -----------------------------------------------------------------------------
# 10) Post‐auth banner (logo + name)
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="banner">
  {logo_html}
  <div class="user-name">{first} {last}</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 11) Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-container">
  <h1>MathPath AI</h1>
  <p>Your Personal Guide to Cal Poly's Math Placement System</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 12) Chat container + dynamic placeholder
# -----------------------------------------------------------------------------
def clean(text: str) -> str:
    return re.sub(r'<Image\b[^>]*?\/>', '', text).strip()

chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # render all stored messages
    for msg in st.session_state.messages:
        c   = clean(msg["content"])
        cls = "user" if msg["role"] == "user" else "assistant"
        st.markdown(f'<div class="chat-message {cls}">{c}</div>', unsafe_allow_html=True)

    # if we need to show the searching bubble, reserve a placeholder
    search_ph = None
    if st.session_state.show_searching:
        search_ph = st.empty()
        search_ph.markdown(
            '<div class="chat-message assistant searching"></div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 13) Input box (pinned)
# -----------------------------------------------------------------------------
def on_submit():
    text = st.session_state.user_input.strip()
    if not text:
        return
    st.session_state.last_input     = text
    st.session_state.show_searching = True
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.user_input = ""

st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.text_input(
    label="Ask a question",
    key="user_input",
    placeholder="Type here…",
    on_change=on_submit,
    label_visibility="hidden"
)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 14) If flagged, do the slow call and replace placeholder with typing effect
# -----------------------------------------------------------------------------
if st.session_state.show_searching and search_ph is not None:
    # fetch full reply
    full_reply = process_user_question(student, st.session_state.last_input)

    # clear the “Searching…” bubble
    search_ph.empty()

    # type out the reply character by character
    typed = ""
    for char in full_reply:
        typed += char
        search_ph.markdown(
            f'<div class="chat-message assistant">{typed}</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.02)  # adjust typing speed here

    # persist and reset
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.session_state.show_searching = False

# -----------------------------------------------------------------------------
# 15) Footer
# -----------------------------------------------------------------------------
st.markdown("""
<div class="footer">
  This chatbox is powered by AI for guidance and recommendations. Responses may contain errors, so always verify with an advisor.
</div>
""", unsafe_allow_html=True)