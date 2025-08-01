import os
import json
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
REGION = os.getenv("AWS_DEFAULT_REGION") or "us-west-2"
KB_ID = os.getenv("KNOWLEDGE_BASE_ID")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
AWS_PROFILE = os.getenv("AWS_PROFILE")

# -----------------------------
# Data loading (schema-faithful JSON)
# -----------------------------
def load_students(path: str = "mock_students.json"):
    """Load student database from JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("mock_students.json must be a JSON object keyed by email.")
        return data
    except Exception as e:
        raise Exception(f"Could not load {path}: {e}")

# -----------------------------
# Bedrock client
# -----------------------------
def get_bedrock_client():
    """Create and return AWS Bedrock client."""
    kw = {"region_name": REGION}
    if AWS_PROFILE:
        kw["profile_name"] = AWS_PROFILE
    try:
        session = boto3.Session(**kw)
        return session.client("bedrock-agent-runtime")
    except Exception as e:
        raise Exception(f"Failed to create Bedrock client: {e}")

# -----------------------------
# Student data processing
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
# Prompt composition
# -----------------------------
def compose_full_prompt(student: dict, user_question: str):
    """Compose a single prompt that sends FULL student record to Bedrock."""
    flags = derive_flags(student)
    
    # Comprehensive system rules for MathPath AI
    system_rules = (
        "You are MathPath AI for Cal Poly math placement.\n"
        "Also, answer gritting and polite to the user's question."
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
        f"Answer clearly. For personal status, rely on the record above. For policy, use the KB and cite sources and give answers pointwise and to the point not too long."
    )
# -----------------------------
def ask_bedrock(prompt: str):
    """Make a call to AWS Bedrock with the given prompt."""
    bedrock = get_bedrock_client()
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
    

    # Add citations from Bedrock response
    for c in resp.get("citations", []) or []:
        for ref in c.get("retrievedReferences", []) or []:
            loc = (ref.get("location", {}) or {}).get("s3Location", {}) or {}
            uri = loc.get("uri") or (ref.get("metadata", {}) or {}).get("source")
            if uri and uri not in citations:
                citations.append(uri)
    return answer, citations[:5]

# -----------------------------
# Main processing function
# -----------------------------
def process_user_question(student: dict, user_question: str):
    """Main function to process a user question and return response with citations."""
    try:
        prompt = compose_full_prompt(student, user_question)
        answer, citations = ask_bedrock(prompt)
        if citations:
            answer += "\n\n**Sources:**\n" + "\n".join(f"- {u}" for u in citations)
        return answer
    except Exception as e:
        return f"Error: {e}"

# -----------------------------
# Student authentication
# -----------------------------
def authenticate_student(email: str, student_db: dict):
    """Authenticate a student by email and return their data."""
    email = email.strip().lower()
    student = student_db.get(email)
    if not student:
        return None, f"No student found for '{email}'."
    return student, None

# -----------------------------
# Environment validation
# -----------------------------
def validate_environment():
    """Validate that all required environment variables are set."""
    if not KB_ID or not MODEL_ID:
        raise Exception("Missing env vars: KNOWLEDGE_BASE_ID and/or BEDROCK_MODEL_ID")
    return True 