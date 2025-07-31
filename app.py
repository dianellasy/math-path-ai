import os
import streamlit as st
from anthropic import Client
from dotenv import load_dotenv
import base64

# 1. Helper: Load logo.png as base64                                       
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = img_to_base64("calpoly-logo.png")



# 2. Load API key & init Anthropic                                         
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic = Client(api_key=ANTHROPIC_API_KEY)


# 3. Streamlit page config                                                 
st.set_page_config(
    page_title="MathPath AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 4. Custom CSS (including banner styles, background & top padding)         
st.markdown("""
<style>
  /* push main content below the fixed banner */
  .appview-container .main {
    padding-top: 80px;
  }

  /* banner styling */
  .banner {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 80px;
    background-color: #8EAB9D;
    display: flex;
    align-items: center;
    padding: 0 20px;
    box-sizing: border-box;
    z-index: 1000;
  }
  .banner img {
    height: 60px;
    margin-right: 20px;
  }
  .banner h1 {
    margin: 0;
    font-size: 2rem;
    color: white;
  }

  /* Set the entire app background */
  body, .stApp {
    background-color: #154734 !important;
  }

  /* rest of your existing CSS */
  .chat-container {
    padding-bottom: 80px;
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
    bottom: 0; left: 0;
    width: 100%;
    background-color: white;
    padding: 10px 20px;
    box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
  }
</style>
""", unsafe_allow_html=True)


# 5. Render the fixed banner                                                
st.markdown(f"""
<div class="banner">
  <img src="data:image/png;base64,{logo_b64}" alt="Logo">
  <h1>MathPath AI</h1>
</div>
""", unsafe_allow_html=True)


# 6. Initialize chat history                                                
if "messages" not in st.session_state:
    st.session_state.messages = []


# 7. Claude helper                                                          
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

# 8. Handle submissions                                                     
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


# 9. Display chat                                                           
chat_area = st.container()
with chat_area:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_class = "user" if msg["role"] == "user" else "assistant"
        bubble = f'<div class="chat-message {role_class}">{msg["content"]}</div>'
        st.markdown(bubble, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 10. Input bar                                                             
with st.container():
    st.markdown('<div class="input-bar">', unsafe_allow_html=True)
    st.text_input(
        label="Ask a question",
        key="user_input",
        placeholder="How may I assist you today?",
        on_change=handle_submit,
        label_visibility="hidden"
    )
    st.markdown('</div>', unsafe_allow_html=True)