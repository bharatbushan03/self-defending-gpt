from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.prompt import PromptResponse, PromptRequest
from app.security.analyzer import analyze_prompt
from app.security.decision import make_decision
from app.services.logger import log_event, get_logs
from app.services.trust import update_trust, get_or_create_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Self-Defending GPT Backend Running"}

@app.post("/analyze-prompt", response_model=PromptResponse)
def analyze(request: PromptRequest):
    analysis = analyze_prompt(request.prompt)

    trust_score = update_trust(request.user_id, analysis["label"])

    decision = make_decision(analysis, trust_score)
    
    log_event(request.prompt, analysis, decision)

    return {
        **analysis,
        **decision,
        "trust_score": trust_score
    }

@app.get("/logs")
def fetch_logs():
    return get_logs()