"""LangGraph workflow definition.

Graph:
  StyleExtractor → Verifier → Generator → Output

Two entry points:
  1. extract_and_verify(tweets, account)   — extract style + verify text
  2. generate_in_style(profile, prompt)     — generate text in extracted style
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Any


class GraphState(TypedDict, total=False):
    """Shared state passed through pipeline nodes."""
    tweets: list[Any]
    account: str
    style_profile: Any
    extraction_confidence: float
    text: str
    generated_text: str
    generation_prompt: str
    max_tokens: int
    verification_score: float
    is_consistent: bool
    verification_details: dict
    output: dict
    error: str


from app.agents.extractor import style_extractor_node
from app.agents.verifier import verifier_node
from app.agents.generator import generator_node
from app.agents.output import output_node


def build_workflow() -> StateGraph:
    """Build the extraction ➜ verification ➜ generation pipeline."""

    workflow = StateGraph(GraphState)

    # Register nodes
    workflow.add_node("StyleExtractor", style_extractor_node)
    workflow.add_node("Verifier", verifier_node)
    workflow.add_node("Generator", generator_node)
    workflow.add_node("Output", output_node)

    # Extraction path: Extractor ➜ Output
    workflow.set_entry_point("StyleExtractor")
    workflow.add_edge("StyleExtractor", "Output")
    workflow.add_edge("Output", END)

    return workflow.compile()


# ----- Convenience runners -----

def run_extraction(tweets: list[Any], account: str) -> dict:
    """Run style extraction on account tweets."""
    app = build_workflow()
    result = app.invoke({
        "tweets": tweets,
        "account": account,
    })
    output = result.get("output", {})
    return output


def run_generation(profile: Any, prompt: str, account: str, max_tokens: int = 500) -> dict:
    """Generate text in a given style profile."""
    workflow = StateGraph(GraphState)
    workflow.add_node("Generator", generator_node)
    workflow.add_node("Output", output_node)
    workflow.set_entry_point("Generator")
    workflow.add_edge("Generator", "Output")
    workflow.add_edge("Output", END)
    app = workflow.compile()

    result = app.invoke({
        "style_profile": profile,
        "generation_prompt": prompt,
        "account": account,
        "max_tokens": max_tokens,
    })
    output = result.get("output", {})
    return output


def run_verification(text: str, account: str) -> dict:
    """Check if text matches account style."""
    workflow = StateGraph(GraphState)
    workflow.add_node("Verifier", verifier_node)
    workflow.add_node("Output", output_node)
    workflow.set_entry_point("Verifier")
    workflow.add_edge("Verifier", "Output")
    workflow.add_edge("Output", END)
    app = workflow.compile()

    result = app.invoke({
        "text": text,
        "account": account,
    })
    output = result.get("output", {})
    return output
