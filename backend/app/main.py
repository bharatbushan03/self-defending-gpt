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
from app.services.logging_service import log_security_event, get_logs as get_logs_service
from app.models.log import SecurityLog

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

class PromptAnalysisRequest(BaseModel):
    prompt: str
    user_id: str

class PromptAnalysisResponse(BaseModel):
    analysis: Dict
    user_trust: Dict
    decision: Decision

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

@app.post("/analyze-prompt", response_model=PromptAnalysisResponse, tags=["Security"])
async def analyze_prompt_endpoint(request: PromptAnalysisRequest):
    """
    Analyzes a prompt, updates trust score, makes a decision, and logs the event.
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
    log_security_event(
        user_id=request.user_id,
        prompt=request.prompt,
        analysis=analysis_result,
        decision=decision.dict(),
        user_trust=user_trust_info
    )

    # Remove MongoDB's internal _id for cleaner API response
    if "_id" in user_trust_info:
        del user_trust_info["_id"]

    return {
        "analysis": analysis_result,
        "user_trust": user_trust_info,
        "decision": decision
    }

@app.get("/logs", response_model=List[SecurityLog], tags=["Monitoring"])
async def get_logs_endpoint(limit: int = 100):
    """
    Retrieves the latest security event logs.
    """
    return get_logs_service(limit)







