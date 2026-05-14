from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pydantic import BaseModel

from app.core.db import connect_to_mongo, close_mongo_connection, ping_database
from app.security.rule_analyzer import analyze_prompt as rule_based_analysis
from app.security.nemotron_analyzer import analyze_prompt_with_nemotron as nemotron_analysis

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

@app.post("/analyze-prompt/rules", tags=["Security"])
async def analyze_prompt_rules_endpoint(request: PromptAnalysisRequest):
    """
    Analyzes a prompt using the rule-based security analyzer.
    """
    return rule_based_analysis(request.prompt)

@app.post("/analyze-prompt/nemotron", tags=["Security"])
async def analyze_prompt_nemotron_endpoint(request: PromptAnalysisRequest):
    """
    Analyzes a prompt using the Nemotron AI security classifier.
    """
    return nemotron_analysis(request.prompt)



