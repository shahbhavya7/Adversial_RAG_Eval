import os
import sys

# 1. Disable Hugging Face symlinks warning as requested
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Add the parent directory to sys.path so we can import adv_rag_eval regardless of where uvicorn is started
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

# Import the local evaluation library
try:
    from adv_rag_eval.evaluator import evaluate_answer
except ImportError as e:
    print(f"Failed to import adv_rag_eval: {e}. Please ensure it is installed or accessible.")
    # For scaffolding, define a dummy if we can't load the real one
    def evaluate_answer(context: str, generated_answer: str) -> dict:
        return {"error": "adv_rag_eval module not found", "hallucination_detected": False, "reasoning": "N/A"}

app = FastAPI(title="Adversarial RAG Evaluator API", version="1.0.0")

# Configure CORS to allow Vite dev server (default port 5173)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel):
    context: str
    answer: str

SECRET_API_KEY = "sk-adv-rag-eval-enterprise-777"
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=403, detail="Access Denied: Invalid API Key")
    
    if api_key.startswith("Bearer "):
        api_key = api_key.replace("Bearer ", "", 1)
        
    if api_key != SECRET_API_KEY:
        raise HTTPException(status_code=403, detail="Access Denied: Invalid API Key")
    return api_key

@app.post("/evaluate")
async def evaluate(request: EvaluationRequest, api_key: str = Depends(verify_api_key)):
    """
    Evaluates the given answer against the context.
    """
    try:
        # Run the evaluator
        result = evaluate_answer(request.context, request.answer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Serve the production React frontend
app.mount("/", StaticFiles(directory="dist", html=True), name="static")
