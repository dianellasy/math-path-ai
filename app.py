import os
import streamlit as st
from anthropic import Client
from dotenv import load_dotenv
import base64

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 1. Helper: Load logo.png as base64                                       │
# └────────────────────────────────────────────────────────────────────────────┘
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = img_to_base64("calpoly-logo.png")


# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 2. Load API key & init Anthropic                                         │
# └────────────────────────────────────────────────────────────────────────────┘
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic = Client(api_key=ANTHROPIC_API_KEY)

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 3. Streamlit page config                                                 │
# └────────────────────────────────────────────────────────────────────────────┘
st.set_page_config(
    page_title="MathPath AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 4. Custom CSS (banner + title + background + padding + input-bar offset) │
# └────────────────────────────────────────────────────────────────────────────┘
st.markdown("""
<style>
  /* push main content below banner */
  .appview-container .main {
    padding-top: 80px;
  }

  /* absolutely center title */
  .page-title {
    position: absolute;
    top: 40%;              /* tweak this % to taste */
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60%;
    text-align: center;
    color: white;
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
    z-index: 1001;
  }

  /* absolutely center input bar just below title */
  .input-bar {
    position: absolute;
    top:  Fifty%;          /* about 10% below the title above */
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60%;
    padding: 10px 0 !important;
    background-color: transparent !important;
    box-shadow: none !important;
    z-index: 1001;
  }
  .input-bar input {
    width: 100% !important;
    box-sizing: border-box;
  }

  /* chat scroll area (if you use it) */
  .chat-container { … }

  /* keep footer stuck to the bottom */
  .footer {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    text-align: center;
    color: #DDDDDD;
    font-size: 0.8rem;
    z-index: 1001;
  }

  /* background */
  body, .stApp { background-color: #154734 !important; }
</style>

""", unsafe_allow_html=True)

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 5. Render the fixed banner (logo only)                                     │
# └────────────────────────────────────────────────────────────────────────────┘
st.markdown(f"""
<div class="banner">
  <img src="data:image/png;base64,{logo_b64}" alt="Logo">
</div>
""", unsafe_allow_html=True)

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 6. Render the title underneath the banner                                  │
# └────────────────────────────────────────────────────────────────────────────┘
st.markdown("""
<div class="page-title">
  MathPath AI
</div>
""", unsafe_allow_html=True)

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 7. Initialize chat history                                                │
# └────────────────────────────────────────────────────────────────────────────┘
if "messages" not in st.session_state:
    st.session_state.messages = []

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 8. Claude helper                                                          │
# └────────────────────────────────────────────────────────────────────────────┘
def get_claude_response(prompt: str) -> str:
    completion = anthropic.completions.create(
        model="claude-3",
        prompt=(
            f"{anthropic.HUMAN_PROMPT} {prompt}\n\n"
            f"{anthropic.AI_PROMPT}"
        ),
        max_tokens_to_sample=500,
        temperature=0.2,
    )
    return completion.completion.strip()

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 9. Handle submissions                                                     │
# └────────────────────────────────────────────────────────────────────────────┘
def handle_submit():
    user_text = st.session_state.user_input.strip()
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})
    st.session_state.user_input = ""

    prompt = "\n".join(
        f"{'Human' if m['role']=='user' else 'Assistant'}: {m['content']}"
        for m in st.session_state.messages
    )
    ai_reply = get_claude_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 10. Display chat                                                           │
# └────────────────────────────────────────────────────────────────────────────┘
chat_area = st.container()
with chat_area:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        cls = "user" if msg["role"] == "user" else "assistant"
        bubble = f'<div class="chat-message {cls}">{msg["content"]}</div>'
        st.markdown(bubble, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 11. Render footer disclaimer                                              │
# └────────────────────────────────────────────────────────────────────────────┘
st.markdown("""
<div class="footer">
  This chatbox is powered by AI for guidance and recommendations. Responses may contain errors. Always verify with an advisor.
</div>
""", unsafe_allow_html=True)

# ┌────────────────────────────────────────────────────────────────────────────┐
# │ 12. Input bar                                                             │
# └────────────────────────────────────────────────────────────────────────────┘
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