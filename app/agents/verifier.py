"""Verifier Agent.

Receives a text + account name, queries the account's FAISS index,
returns a similarity score indicating whether the text matches the
account's learned style.
"""

import numpy as np
from app import config
from app.db.faiss_index import FaissIndexManager


def verifier_node(state: dict) -> dict:
    """
    LangGraph node: checks a piece of text against the account's
    stored style index and returns a similarity score.
    """
    text = state.get("text", state.get("generated_text", ""))
    account = state.get("account", "unknown")

    if not text:
        return {
            **state,
            "verification_score": 0.0,
            "is_consistent": False,
            "verification_details": {"error": "No text provided"},
        }

    try:
        index_manager = FaissIndexManager(account, config.INDICES_DIR)

        if not index_manager.index_exists():
            return {
                **state,
                "verification_score": 0.5,
                "is_consistent": True,
                "verification_details": {
                    "note": f"No index found for {account}, defaulting to neutral",
                },
            }

        score, details = index_manager.query(text)
        is_consistent = score >= 0.6

        return {
            **state,
            "verification_score": score,
            "is_consistent": is_consistent,
            "verification_details": details,
        }

    except Exception as e:
        return {
            **state,
            "verification_score": 0.0,
            "is_consistent": False,
            "verification_details": {"error": str(e)},
        }
