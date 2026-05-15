from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, List

from app.core.db import connect_to_mongo, close_mongo_connection, ping_database
from app.security.risk_engine import calculate_hybrid_risk
from app.services.trust_service import update_trust_score
from app.security.decision_engine import make_decision
from app.models.decision import Decision
from app.services.logging_service import create_security_log, get_security_logs
from app.models.log import SecurityLog
from app.services.chat_service import get_chatbot_response
from app.models.chat import ChatRequest, ChatResponse

load_dotenv()

app = FastAPI(
    title="Self-Defending GPT API",
    description="API for the Self-Defending GPT security gateway.",
    version="0.1.0"
)

# Add startup and shutdown event handlers
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)


# CORS Configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
async def root():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

@app.get("/db-health", tags=["Health Check"])
async def db_health():
    """
    Database health check endpoint.
    """
    is_connected = await ping_database()
    if is_connected:
        return {"status": "ok", "database_connection": "successful"}
    return {"status": "error", "database_connection": "failed"}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def secure_chat_endpoint(request: ChatRequest):
    """
    Handles a user chat request through the full security pipeline.
    """
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required.")

    # 1. Analyze the prompt
    analysis_result = calculate_hybrid_risk(request.prompt, request.user_id)
    
    # 2. Update user trust score
    user_trust_info = update_trust_score(request.user_id, analysis_result["final_label"])
    
    # 3. Make a final decision
    decision = make_decision(
        risk_score=analysis_result["final_risk_score"],
        trust_score=user_trust_info["trust_score"]
    )

    # 4. Log the security event
    log_entry = SecurityLog(
        user_id=request.user_id,
        prompt=request.prompt,
        label=analysis_result["final_label"],
        risk_score=analysis_result["final_risk_score"],
        action=decision.action,
        reauth_required=decision.reauth_required,
        reasons=analysis_result["reasons"],
        attack_type=analysis_result["attack_type"],
        trust_score=user_trust_info["trust_score"]
    )
    create_security_log(log_entry)

    # 5. Handle BLOCK action
    if decision.action == "BLOCK":
        return ChatResponse(
            response="Your request has been blocked for security reasons.",
            action=decision.action,
            message=decision.message,
            risk_score=analysis_result["final_risk_score"],
            trust_score=user_trust_info["trust_score"],
            reauth_required=decision.reauth_required
        )

    # 6. Handle ALLOW or WARN action
    chatbot_response = get_chatbot_response(request.prompt)

    return ChatResponse(
        response=chatbot_response,
        action=decision.action,
        message=decision.message,
        risk_score=analysis_result["final_risk_score"],
        trust_score=user_trust_info["trust_score"],
        reauth_required=decision.reauth_required
    )


@app.get("/logs", response_model=List[Dict], tags=["Logging"])
async def get_logs_endpoint(limit: int = 100):
    """
    Retrieves the latest security logs.
    """
    logs = get_security_logs(limit)
    # The _id is already handled in the service, but as a safeguard:
    for log in logs:
        if "_id" in log:
            log["_id"] = str(log["_id"])
    return logs







