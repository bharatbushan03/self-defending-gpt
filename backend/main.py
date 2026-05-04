import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from app.models.prompt import PromptResponse, PromptRequest
    from app.models.chat import ChatResponse
    from app.security.analyzer import analyze_prompt
    from app.security.decision import make_decision
    from app.services.logger import log_event, get_logs
    from app.services.trust import update_trust, get_or_create_user
    from app.services.chat import generate_response
    from app.services.memory import save_message, get_chat_history
    from app.services.analytics import (
        get_risk_distribution,
        get_attack_trends,
        get_top_risky_users,
    )
except ModuleNotFoundError:
    from backend.app.models.prompt import PromptResponse, PromptRequest
    from backend.app.models.chat import ChatResponse
    from backend.app.security.analyzer import analyze_prompt
    from backend.app.security.decision import make_decision
    from backend.app.services.logger import log_event, get_logs
    from backend.app.services.trust import update_trust, get_or_create_user
    from backend.app.services.chat import generate_response
    from backend.app.services.memory import save_message, get_chat_history
    from backend.app.services.analytics import (
        get_risk_distribution,
        get_attack_trends,
        get_top_risky_users,
    )

app = FastAPI()

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins.split(",") if origin.strip()],
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

@app.post("/chat", response_model = ChatResponse)
def chat(request: PromptRequest):
    analysis = analyze_prompt(request.prompt)
    trust_score = update_trust(request.user_id, analysis["label"])
    decision = make_decision(analysis, trust_score)
    log_event(request.prompt, analysis, decision)

    if decision["action"] == "BLOCK":
        return {
            "response": None,
            "action": decision["action"],
            "message": decision["message"],
            "risk_score": analysis["risk_score"],
            "trust_score": trust_score
        }
    
    save_message(request.user_id, "user", request.prompt)

    ai_response = generate_response(request.user_id, request.prompt)

    save_message(request.user_id, "assistant", ai_response)

    return {
        "response": ai_response,
        "action": decision["action"],
        "message": decision["message"],
        "risk_score": analysis["risk_score"],
        "trust_score": trust_score
    }

@app.get("/analytics/risk-distribution")
def risk_distribution():
    return get_risk_distribution()

@app.get("/analytics/attack-trends")
def attack_trends():
    return get_attack_trends()

@app.get("/analytics/top-users")
def top_users():
    return get_top_risky_users()

@app.get("/logs")
def fetch_logs():
    return get_logs()