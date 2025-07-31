import os
import streamlit as st
from anthropic import Client
from dotenv import load_dotenv
import base64


def set_bg_local(image_path):
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_bg_local("background.jpg")


# 1. Load API key
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# 2. Initialize Anthropic client
anthropic = Client(api_key=ANTHROPIC_API_KEY)

# 3. Page config
st.set_page_config(
    page_title="MathPath AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 4. Custom CSS for bubbles and layout
st.markdown("""
<style>
body {
    background-color: white;
}
.header {
  position: relative;
  height: 60px;       /* adjust as needed */
  background-color: white;
  margin-bottom: 20px;
}
.header h1 {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  font-size: 2.5rem;
}
.header img {
  position: absolute;
  right: 20px;        /* space from the right edge */
  top: 50%;
  transform: translateY(-50%);
  height: 50px;
}
.chat-container {
    padding-bottom: 80px;  /* leave room for input bar */
}
.chat-message {
    padding: 12px;
    border-radius: 15px;
    max-width: 70%;
    margin: 8px 0;
    word-wrap: break-word;
}
.user {
    background-color: #498555;
    margin-left: auto;
    margin-right: 0;
}
.assistant {
    background-color: #F0F0F0;
    margin-left: 0;
    margin-right: auto;
}
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: white;
    padding: 10px 20px;
    box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# 5. Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

# 6. Render header on every run
with st.container():
    st.markdown(
    """
    <style>
      .header {
        position: relative;
        text-align: center;
        padding: 1rem 0;
      }
    </style>

    <div class="header">
      <h1>MathPath AI</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# 7. Function to query Anthropic Claude
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

# 8. Submission handling
def handle_submit():
    user_text = st.session_state.user_input.strip()
    if not user_text:
        return

    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_text})
    # Clear input box
    st.session_state.user_input = ""

    # Get AI reply
    full_prompt = "\n".join(
        f"{'Human' if msg['role']=='user' else 'Assistant'}: {msg['content']}"
        for msg in st.session_state.messages
    )
    ai_reply = get_claude_response(full_prompt)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# 9. Display chat history
chat_area = st.container()
with chat_area:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_class = "user" if msg["role"] == "user" else "assistant"
        bubble = f'<div class="chat-message {role_class}">{msg["content"]}</div>'
        st.markdown(bubble, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 10. Input bar at the bottom
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