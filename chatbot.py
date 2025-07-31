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

def query_bedrock(prompt: str) -> str:
    bedrock = get_bedrock_client()
    kb_id = os.getenv("KNOWLEDGE_BASE_ID")
    model_id = os.getenv("BEDROCK_MODEL_ID")

    # Load prompt from external file
    with open("system_prompt.txt", "r") as file:
        system_prompt = file.read()

    try:
        response = bedrock.retrieve_and_generate(
            input={
                'text': f"{system_prompt}\n\nUser question: {prompt}"
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{model_id}'
                }
            }
        )
        return response['output']['text']
    except Exception as e:
        return f"Error: {e}"
