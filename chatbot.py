import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def get_bedrock_client():
    return boto3.client(
        'bedrock-agent-runtime',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

def query_bedrock(user_prompt: str) -> str:
    bedrock = get_bedrock_client()
    kb_id = os.getenv("KNOWLEDGE_BASE_ID")
    model_id = os.getenv("BEDROCK_MODEL_ID")

    # Load system prompt from external file
    with open("system_prompt.txt", "r") as file:
        system_prompt = file.read().strip()

    # Construct the full prompt clearly separating instructions and conversation
    input_text = f"""You are MathPath AI, a friendly and formal AI assistant for CSU Cal Poly San Luis Obispo who helps students with math placement questions.

Instructions:
{system_prompt}

Conversation:
User: {user_prompt}
MathPath AI:"""

    try:
        response = bedrock.retrieve_and_generate(
            input={
                'text': input_text
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{model_id}'
                }
            }
        )
        return response['output']['text'].strip()
    except Exception as e:
        return f"Error: {e}"


def is_off_topic(user_input: str) -> bool:
    off_topic_keywords = [
        "hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye", "what's up", "how are you",
        "housing", "dining", "financial aid", "sports", "clubs", "parking"
    ]
    user_input_lower = user_input.lower().strip()
    # Simple check if input is exactly a greeting or contains off-topic keywords
    return any(word in user_input_lower for word in off_topic_keywords)

def get_fallback_response(user_input: str) -> str:
    greetings = {"hi", "hello", "hey", "is anyone there", "good morning", "good afternoon", "good evening"}
    if user_input.lower().strip() in greetings:
        return "Hi there! I’m MathPath AI. I help students with math placement questions at Cal Poly. How can I assist you today?"
    else:
        return ("I’m here to help with math placement questions at Cal Poly. "
                "For other topics, please contact the appropriate campus office or visit the Cal Poly website.")

def query_mathpath(user_prompt: str) -> str:
    # If the input is off-topic or simple greeting, return fallback immediately
    if is_off_topic(user_prompt):
        return get_fallback_response(user_prompt)
    
    # Otherwise, query Bedrock model
    return query_bedrock(user_prompt)
