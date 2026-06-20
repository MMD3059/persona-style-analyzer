"""Output Agent.

Formats and persists the results from the pipeline.
Saves style profiles to JSON and prepares API responses.
"""

import json
import os
from datetime import datetime
from app import config


def output_node(state: dict) -> dict:
    """LangGraph node: saves results and prepares the final output."""
    profile = state.get("style_profile")
    account = state.get("account", "unknown")

    result = {
        "account": account,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
    }

    if profile:
        os.makedirs(config.PROFILES_DIR, exist_ok=True)
        profile_path = os.path.join(config.PROFILES_DIR, f"{account}.json")

        profile_dict = profile.model_dump(mode="json")
        profile_dict["extraction_confidence"] = state.get("extraction_confidence", 0.0)

        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile_dict, f, ensure_ascii=False, indent=2)

        result["style_profile"] = profile_dict
        result["profile_saved_to"] = profile_path

    if state.get("generated_text"):
        result["generated_text"] = state["generated_text"]

    if state.get("verification_score") is not None:
        result["verification"] = {
            "score": state["verification_score"],
            "is_consistent": state.get("is_consistent", False),
            "details": state.get("verification_details", {}),
        }

    result["extraction_confidence"] = state.get("extraction_confidence", 0.0)
    result["tweet_count"] = len(state.get("tweets", []))

    return {**state, "output": result}
