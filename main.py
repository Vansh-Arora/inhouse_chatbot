from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import os
import requests

app = FastAPI()

# Load Together API key from environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# TOGETHER_API_KEY = '4ad46d352e8cc4be86e2285c7dabcfddc1eb95f706bc739d7f7bf9a9dcc3dc11'
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

# Barclays-grade redaction patterns
PATTERNS = {
    "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "AADHAAR": r"\b\d{4}\s\d{4}\s\d{4}\b",
    "SORT_CODE": r"\b\d{2}-\d{2}-\d{2}\b",
    "IBAN": r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
    "CARD": r"\b(?:\d{4}[- ]?){4}\b",
    "EMAIL": r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b",
    "ACCOUNT_NO": r"\b\d{8,18}\b",
    "SWIFT": r"\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b",
    "BARCLAYS_ID": r"\bB[0-9]{6,}\b",
    "JIRA": r"\b[A-Z]{2,5}-\d{1,6}\b",
    "ENV_VARS": r"\b(AWS|GCP|PROD|STAGE|UAT)_.*?\b"
}

BLOCKED_KEYWORDS = [
    "audit", "incident", "password", "api_key", "secret", "prod", "token",
    "confidential", "fraud", "pbu", "barcap"
]

# Redact sensitive patterns
def redact_barclays(text: str) -> str:
    for label, pattern in PATTERNS.items():
        text = re.sub(pattern, f"[REDACTED {label}]", text, flags=re.IGNORECASE)
    for word in BLOCKED_KEYWORDS:
        text = re.sub(fr"\b{re.escape(word)}\b", "[REDACTED]", text, flags=re.IGNORECASE)
    return text

# Check if text contains sensitive info
def is_sensitive_barclays(text: str) -> bool:
    for pattern in PATTERNS.values():
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return any(word in text.lower() for word in BLOCKED_KEYWORDS)

# Pydantic request model
class ChatRequest(BaseModel):
    prompt: str
    user_role: str = "employee"

# Pydantic response model
class ChatResponse(BaseModel):
    response: str

# Query Together AI model
def query_model(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error querying model: {str(e)}"

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if is_sensitive_barclays(request.prompt):
        raise HTTPException(status_code=403, detail="Sensitive bank information detected.")

    safe_prompt = redact_barclays(request.prompt)
    model_output = query_model(safe_prompt)
    safe_response = redact_barclays(model_output)

    return ChatResponse(response=safe_response)

@app.get("/")
def root():
    return {"status": "Barclays secure chatbot is running."}
