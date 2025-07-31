import os
import re
import time
import base64
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
REGION = os.getenv("AWS_DEFAULT_REGION") or "us-west-2"
KB_ID = os.getenv("KNOWLEDGE_BASE_ID")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
AWS_PROFILE = os.getenv("AWS_PROFILE")

if not KB_ID or not MODEL_ID:
    st.error("Missing env vars: KNOWLEDGE_BASE_ID and/or BEDROCK_MODEL_ID")
    st.stop()

# -----------------------------
# Data loading (schema-faithful JSON)
# -----------------------------
def load_students(path: str = "mock_students.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("mock_students.json must be a JSON object keyed by email.")
        return data
    except Exception as e:
        st.error(f"Could not load {path}: {e}")
        st.stop()

STUDENT_DB = load_students()

# -----------------------------
# Bedrock client
# -----------------------------
def bedrock_client():
    kw = {"region_name": REGION}
    if AWS_PROFILE:
        kw["profile_name"] = AWS_PROFILE
    try:
        import boto3
        session = boto3.Session(**kw)
        return session.client("bedrock-agent-runtime")
    except Exception as e:
        st.error(f"Failed to create Bedrock client: {e}")
        st.stop()

bedrock = bedrock_client()

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
student = STUDENT_DB.get(email)
if not student:
    st.warning(f"No student found for '{email}'.")
    with st.expander("Available test emails"):
        st.json(list(STUDENT_DB.keys()))
    if st.button("Use a different email"):
        del st.session_state["student_email"]
        st.rerun()
    st.stop()

st.caption(f"Signed in as: {email}")

# -----------------------------
# Optional: derive a concise summary to help the model
# -----------------------------
def derive_flags(student: dict):
    """Normalize schema-like JSON and derive concise status booleans/labels."""
    person = (student.get("person") or {}) if isinstance(student.get("person"), dict) else {}
    first = (person.get("first_name") or "").strip()
    last = (person.get("last_name") or "").strip()
    full_name = (f"{first} {last}".strip()) or "Unknown"

    apps = student.get("applications") or []
    if not isinstance(apps, list):
        apps = []
    program = plan = status = "Unknown"
    if apps:
        try:
            latest = sorted(apps, key=lambda a: (a or {}).get("submission_date", ""))[-1]
        except Exception:
            latest = apps[-1]
        program = (latest or {}).get("program", program) or program
        plan    = (latest or {}).get("plan", plan) or plan
        status  = (latest or {}).get("status", status) or status

    raw_docs = student.get("documents") or []
    if not isinstance(raw_docs, list):
        raw_docs = []
    doc_types = set()
    for item in raw_docs:
        t = None
        if isinstance(item, dict):
            t = item.get("type")
        elif isinstance(item, str):
            t = item
        if isinstance(t, str):
            doc_types.add(t.strip().lower())
    sat_received = any(x in doc_types for x in {"sat", "sat score"})
    ap_received  = any(x in doc_types for x in {"ap", "ap score", "ap scores"})
    transcript_received = "transcript" in doc_types

    raw_events = student.get("events") or []
    if not isinstance(raw_events, list):
        raw_events = []
    events_by_id = {}
    for e in raw_events:
        if isinstance(e, dict):
            ev_id = e.get("event_id")
            if isinstance(ev_id, str):
                events_by_id[ev_id] = e
    raw_att = student.get("event_attendance") or []
    if not isinstance(raw_att, list):
        raw_att = []
    mape_status = "not scheduled"
    for att in raw_att:
        if not isinstance(att, dict):
            continue
        ev_id = att.get("event_id")
        title = ""
        if isinstance(ev_id, str):
            title = (events_by_id.get(ev_id, {}).get("title") or "")
        title_l = title.lower()
        if "mape" in title_l:
            if "online" in title_l:
                mape_status = "online"; break
            if "in-person" in title_l or "in person" in title_l:
                mape_status = "in-person"; break

    return {
        "name": full_name,
        "program": program,
        "plan": plan,
        "status": status,
        "sat_received": sat_received,
        "ap_received": ap_received,
        "transcript_received": transcript_received,
        "mape_status": mape_status,
    }

# -----------------------------
# Compose a single prompt that sends FULL student record to Bedrock
# -----------------------------
def compose_full_prompt(student: dict, user_question: str):
    flags = derive_flags(student)
    # Minimal, clear instructions. Adjust to your mentor's guidance as needed.
    system_rules = (
        "You are MathPath AI for Cal Poly math placement.\n"
        "Use the FULL student record below to answer personal status questions (SAT/AP/transcript/MAPE).\n"
        "Also use the Knowledge Base for official policy/FAQ. If the KB lacks a policy, say you don't know.\n"
        "Prefer exact data from the student record over assumptions. Cite sources only for policy content from the KB."
    )
    student_json = json.dumps(student, indent=2, ensure_ascii=False)
    flags_text = (
        f"Derived Summary:\n"
        f"  Program: {flags['program']}\n"
        f"  SAT Received: {flags['sat_received']}\n"
        f"  AP Scores Received: {flags['ap_received']}\n"
        f"  Transcript Received: {flags['transcript_received']}\n"
        f"  MAPE Status: {flags['mape_status']}\n"
    )
    return (
        f"{system_rules}\n\n"
        f"Full Student Record (JSON):\n{student_json}\n\n"
        f"{flags_text}\n"
        f"Student Question:\n{user_question}\n\n"
        f"Answer clearly. For personal status, rely on the record above. For policy, use the KB and cite sources."
    )

# -----------------------------
# Bedrock KB call
# -----------------------------
def ask_bedrock(prompt: str):
    resp = bedrock.retrieve_and_generate(
        input={"text": prompt},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KB_ID,
                "modelArn": f"arn:aws:bedrock:{REGION}::foundation-model/{MODEL_ID}",
            },
        },
    )
    answer = (resp.get("output", {}) or {}).get("text", "") or "(No answer)"
    citations = []
    for c in resp.get("citations", []) or []:
        for ref in c.get("retrievedReferences", []) or []:
            loc = (ref.get("location", {}) or {}).get("s3Location", {}) or {}
            uri = loc.get("uri") or (ref.get("metadata", {}) or {}).get("source")
            if uri and uri not in citations:
                citations.append(uri)
    return answer, citations[:5]

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
        try:
            prompt = compose_full_prompt(student, text)
            ans, cites = ask_bedrock(prompt)
            if cites:
                ans += "\n\n**Sources:**\n" + "\n".join(f"- {u}" for u in cites)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"Error: {e}")
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
