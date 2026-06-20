"""Persona Style Analyzer API.

FastAPI server that orchestrates style extraction, verification,
and generation for Arabic social media accounts using Fanar LLM.
"""

from fastapi import FastAPI, HTTPException
from app.models.schemas import (
    ExtractionRequest, ExtractionResponse,
    VerificationRequest, VerificationResponse,
    GenerationRequest, GenerationResponse,
    StyleProfile,
)
from app.graph.workflow import run_extraction, run_generation, run_verification
from app import config
import os
import json

app = FastAPI(
    title="Persona Style Analyzer",
    description="Extract, verify, and generate Arabic social media style profiles using Fanar LLM",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "service": "Persona Style Analyzer",
        "version": "0.1.0",
        "endpoints": {
            "POST /extract": "Extract style profile from tweets",
            "POST /verify": "Check text consistency with account style",
            "POST /generate": "Generate text in account style",
            "GET  /profiles": "List all saved profiles",
            "GET  /profiles/{account}": "Get a specific profile",
        },
    }


@app.post("/extract", response_model=ExtractionResponse)
async def extract_style(req: ExtractionRequest):
    """Extract a style profile from an account's tweets."""
    if not req.tweets:
        raise HTTPException(status_code=400, detail="No tweets provided")

    tweets_dict = [t.model_dump() for t in req.tweets]
    result = run_extraction(tweets_dict, req.account)

    if "error" in result and result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])

    profile_dict = result.get("style_profile", {})
    if isinstance(profile_dict, StyleProfile):
        profile = profile_dict
    else:
        profile = StyleProfile(**profile_dict) if profile_dict else StyleProfile(account=req.account)

    return ExtractionResponse(
        profile=profile,
        confidence=result.get("extraction_confidence", 0.0),
        tweet_count=len(req.tweets),
    )


@app.post("/verify", response_model=VerificationResponse)
async def verify_text(req: VerificationRequest):
    """Check if text matches an account's learned style."""
    result = run_verification(req.text, req.account)

    verification = result.get("verification", {})
    return VerificationResponse(
        account=req.account,
        similarity_score=verification.get("score", 0.0),
        is_consistent=verification.get("is_consistent", False),
        details=verification.get("details", {}),
    )


@app.post("/generate", response_model=GenerationResponse)
async def generate_text(req: GenerationRequest):
    """Generate text in an account's style."""
    # Load profile if exists
    profile_path = os.path.join(config.PROFILES_DIR, f"{req.account}.json")
    profile = None
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
            profile = StyleProfile(**profile_data)

    result = run_generation(profile, req.prompt, req.account, req.max_tokens)

    return GenerationResponse(
        text=result.get("generated_text", ""),
        account=req.account,
        style_adherence=0.7,  # placeholder: real scoring in next iteration
    )


@app.get("/profiles")
async def list_profiles():
    """List all saved style profiles."""
    os.makedirs(config.PROFILES_DIR, exist_ok=True)
    profiles = []
    for fname in os.listdir(config.PROFILES_DIR):
        if fname.endswith(".json"):
            path = os.path.join(config.PROFILES_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                profiles.append({
                    "account": data.get("account", fname.replace(".json", "")),
                    "created_at": data.get("created_at", ""),
                    "confidence": data.get("extraction_confidence", 0.0),
                })
    return {"profiles": profiles, "count": len(profiles)}


@app.get("/profiles/{account}")
async def get_profile(account: str):
    """Get a specific account's style profile."""
    path = os.path.join(config.PROFILES_DIR, f"{account}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Profile for '{account}' not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/indices")
async def list_indices():
    """List all FAISS indices."""
    os.makedirs(config.INDICES_DIR, exist_ok=True)
    indices = []
    for fname in os.listdir(config.INDICES_DIR):
        if fname.endswith(".faiss"):
            account = fname.replace(".faiss", "")
            meta_path = os.path.join(config.INDICES_DIR, f"{account}_meta.json")
            size = 0
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    size = len(json.load(f))
            indices.append({"account": account, "size": size})
    return {"indices": indices, "count": len(indices)}
