import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()
REGION = os.getenv("AWS_DEFAULT_REGION") or "us-west-2"
KB_ID = os.getenv("KNOWLEDGE_BASE_ID")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
AWS_PROFILE = os.getenv("AWS_PROFILE")

def load_students(path: str = "mock_students.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("mock_students.json must be a JSON object keyed by email.")
        return data
    except Exception as e:
        raise Exception(f"Could not load {path}: {e}")

def get_bedrock_client():
    kw = {"region_name": REGION}
    if AWS_PROFILE:
        kw["profile_name"] = AWS_PROFILE
    try:
        session = boto3.Session(**kw)
        return session.client("bedrock-agent-runtime")
    except Exception as e:
        raise Exception(f"Failed to create Bedrock client: {e}")

def derive_flags(student: dict):
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

def compose_full_prompt(student: dict, user_question: str):
    flags = derive_flags(student)
    
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
        f"Answer clearly. For personal status, rely on the record above. For policy, use the KB and cite sources and give answers pointwise and to the point not too long."
    )

def ask_bedrock(prompt: str, user_question: str = ""):
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
    
    for c in resp.get("citations", []) or []:
        for ref in c.get("retrievedReferences", []) or []:
            loc = (ref.get("location", {}) or {}).get("s3Location", {}) or {}
            uri = loc.get("uri") or (ref.get("metadata", {}) or {}).get("source")
            if uri and uri.startswith("https://") and uri not in citations:
                citations.append(uri)
    
    math_placement_kb_used = any("MathPlacementKB.pdf" in citation for citation in citations)
    policy_keywords = ["policy", "policies", "rule", "rules", "requirement", "requirements", "mape", "placement", "exam", "test"]
    is_policy_question = any(keyword in user_question.lower() for keyword in policy_keywords)
    
    if math_placement_kb_used or is_policy_question:
        math_placement_kb_url = "https://math-placement-knowledge-base.s3.us-west-2.amazonaws.com/MathPlacementKB.pdf?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIDnE8OP1DOoHpXHP34ii7Mk5Rq6BaDQcnlr4Q9Nfi7QeAiEAzMzn%2FNYuAWLzxYVpnSs43dbNCfZdAODy5c3AMiTdi6Qq9wQI8%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw5OTQzMDk5NTE4MDAiDOxsmvhgjnirL07vJCrLBLv5mBap1I1cY9sIZ3BtG8QFs9LVIeFSYRNB7YoHol5RIZtXuvFellRsqqF06a1dTO58jCvVDrvgCd3o3OiSkrsFFIYWSx8tdDtLbHYB76FtPbtnN7cQoyS%2Fq66ASf%2Fco4JO3HgiRSWXHdVg87Z4LVGpbMjRHHtHN44%2Fu4N%2BF92Whf6DfdBoXzr3D9N6dMmwc%2BqtqLAJ4Ng4CZhroB1yMCnHyaOpIzse5cPwmYI5s5J7FqW1jfBUZVNuHHgd0%2BdXz%2FJACnfo9jhDZN7CGILfcTp6eqExKP7zS94lkK5Qa2UphIe5z5ngZz3WbgLgRQH51dAA9gkSwCcVLDbtl%2BZU2BCOzgc1CGcjpzvhJ7ul7QIhlbzQ0%2FjSzxO1bvLe4hKa%2FxXI%2Fu3yxeah3BOAc12aOwgu4D8ElWiURqOZ936AQARcV1vu4LDI0PUzJXBn0ZDHGbE051eKzRcFW7j68eelINIwSoIE7vWaUl25ts8OLxRCDLENhEyewtLSus2jJgOdCYVFUYIaAxp5YnAtTHlTzQC9mihir%2FKggEJUC45Yk8icVHXOcAOhP2AlURiBby4BHHQCg1ZsvX5PK1jGUwVIaQpGd2Iq%2BL9YFpnRvVooqvNSeIRGlN7CWfqUOwdzQRhptp%2BczzI27yMoRqv1wiHxLoaYv4%2F2qVgGict7qYqtnZFYY%2BsEtJHzxPe0Rvoi%2BaZQMBu9xp8u%2B2Y74wuhVdLF2qpgSgBswMNVgUwUIjAxB4FdlJ16l5gYhyhiVnnk8UgLMxC%2FsahRxnmyehZjMInys8QGOsUCvE%2Bb6q2LM6psNj6YuJ2zjmFw0twYGvvGADNW9rwa6l6pjdCzeWaA2iZZ45qPKFp03eDkF5PhcCQfW3MpJtF95e7BJ%2FH8Sttx8dhSxiAnvWZsspsDQrLvPLEcexq1rxBBZqxeQ83YjiwS3qXAvkmhTW43LPz5qmZ0zIlBL30VZwDEzB7wl0QvWvsfdwOWR96wd1l%2BSrHRh%2FcDgdfQVyJWViG6D%2BKnPc6Xkt8Vmsns00PlV2VRsXkQah49Dj6yt7SgNl4A9%2FZt%2F5tz%2BEO1UFpynxkE6OKb%2FMzYxWbi6ENLJElbq7thN8zJozZHAWfQgs677i8LOGFcPVXh2Zp26T5nP2EfjC5mfUkmu1aFThQkEK1pGxausUYBKWXZQPgPgSuhOcmt1TztDU1cSMlHK2iiVIQkrKJOfAcmmRWaw%2FuHG2AqwETWjw%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA6PAL52E4F52WC6SQ%2F20250801%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250801T172758Z&X-Amz-Expires=36000&X-Amz-SignedHeaders=host&X-Amz-Signature=0911ab15346c0a3f01f83ee5fac70ee28d9a64aca8f27bea345028e38d5aa739"
        citations.append(math_placement_kb_url)
    return answer, citations[:5]

def process_user_question(student: dict, user_question: str):
    try:
        prompt = compose_full_prompt(student, user_question)
        answer, citations = ask_bedrock(prompt, user_question)
        if citations:
            citation_links = []
            for citation in citations:
                if citation.startswith("https://"):
                    if "MathPlacementKB.pdf" in citation:
                        citation_links.append(f"- [Math Placement KB]({citation})")
                    else:
                        citation_links.append(f"- [Source]({citation})")
                else:
                    citation_links.append(f"- {citation}")
            answer += "\n\nSources:\n" + "\n".join(citation_links)
        return answer
    except Exception as e:
        return f"Error: {e}"

def authenticate_student(email: str, student_db: dict):
    email = email.strip().lower()
    student = student_db.get(email)
    if not student:
        return None, f"No student found for '{email}'."
    return student, None

def validate_environment():
    if not KB_ID or not MODEL_ID:
        raise Exception("Missing env vars: KNOWLEDGE_BASE_ID and/or BEDROCK_MODEL_ID")
    return True 