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
from app.services import memory_service
from app.services import analytics_service

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

    # 5. Handle based on decision
    chatbot_response = ""
    if decision.action == "BLOCK":
        chatbot_response = "Your request has been blocked for security reasons."
    else:
        # If allowed or warned, get conversation history and generate response
        history = memory_service.get_conversation_history(request.user_id)
        chatbot_response = get_chatbot_response(request.prompt, history)
        
        # Store the user message and the assistant's response in history
        memory_service.store_message(request.user_id, "user", request.prompt)
        memory_service.store_message(request.user_id, "assistant", chatbot_response)

    return ChatResponse(
        response=chatbot_response,
        action=decision.action,
        message=decision.message,
        risk_score=analysis_result["final_risk_score"],
        trust_score=user_trust_info["trust_score"],
        reasons=analysis_result["reasons"]
    )


@app.get("/logs", response_model=List[Dict], tags=["Admin"])
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

# --- Analytics Endpoints for SOC Dashboard ---

@app.get("/analytics/summary", tags=["Analytics"])
async def get_summary():
    """Provides a summary of security analytics."""
    return analytics_service.get_summary_analytics()

@app.get("/analytics/risk-distribution", tags=["Analytics"])
async def get_risk_dist():
    """Provides the distribution of requests by risk label."""
    return analytics_service.get_risk_distribution()

@app.get("/analytics/attack-trends", tags=["Analytics"])
async def get_attack_trends_endpoint(days: int = 30):
    """Provides the trend of attacks over the last N days."""
    return analytics_service.get_attack_trends(days)

@app.get("/analytics/top-risky-users", tags=["Analytics"])
async def get_top_users_endpoint(limit: int = 5):
    """Identifies the top N riskiest users."""
    return analytics_service.get_top_risky_users(limit)

@app.get("/analytics/recent-attacks", tags=["Analytics"])
async def get_recent_attacks_endpoint(limit: int = 10):
    """Retrieves the most recent N blocked attacks."""
    return analytics_service.get_recent_attacks(limit)







