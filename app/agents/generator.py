"""Generator Agent.

Uses the account's style profile to generate text in that style.
"""

from app.models.fanar import FanarClient
from app.models.schemas import StyleProfile


GENERATOR_SYSTEM_PROMPT = """You are a style-accurate text generator. Your task is to generate Arabic text that perfectly mimics the communication style of a specific account.

You will receive:
1. The account's STYLE PROFILE (vocabulary, tone, beliefs, red flags)
2. A PROMPT or instruction about what to write

Rules:
- Match vocabulary, sentence structure, and repeated phrases exactly
- Stay within the account's emotional range and formality level
- NEVER cross red flags or use avoided phrases
- Maintain the belief system and stances
- Keep sentence length and punctuation style consistent

Return only the generated text without explanation."""


def generator_node(state: dict) -> dict:
    """LangGraph node: generates text in the account's style."""
    prompt = state.get("generation_prompt", state.get("prompt", ""))
    account = state.get("account", "unknown")
    profile: StyleProfile | None = state.get("style_profile")

    if not prompt:
        return {**state, "generated_text": "", "generation_error": "No prompt"}

    profile_block = _format_profile_for_prompt(profile, account)
    full_prompt = (
        f"Account: {account}\n\n"
        f"Style Profile:\n{profile_block}\n\n"
        f"Generation Task:\n{prompt}"
    )

    try:
        fanar = FanarClient()
        generated = fanar.generate(
            prompt=full_prompt,
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            temperature=0.4,
            max_tokens=state.get("max_tokens", 500),
        )

        return {
            **state,
            "generated_text": generated,
            "generation_account": account,
        }

    except Exception as e:
        return {
            **state,
            "generated_text": "",
            "generation_error": str(e),
        }


def _format_profile_for_prompt(profile: StyleProfile | None, account: str) -> str:
    if profile is None:
        return "No profile available. Generate in neutral formal Arabic."

    lines = []
    lines.append("--- VOCABULARY ---")
    if profile.vocab.repeated_phrases:
        lines.append(f"Repeated phrases: {', '.join(profile.vocab.repeated_phrases)}")
    if profile.vocab.religious_terms:
        lines.append(f"Religious terms: {', '.join(profile.vocab.religious_terms)}")
    if profile.vocab.hashtag_patterns:
        lines.append(f"Hashtag patterns: {', '.join(profile.vocab.hashtag_patterns)}")
    if profile.vocab.unique_terms:
        lines.append(f"Unique terms: {', '.join(profile.vocab.unique_terms)}")

    lines.append("\n--- TONE ---")
    lines.append(f"Formality: {profile.tone.formality}")
    lines.append(f"Sentiment: {profile.tone.sentiment}")
    if profile.tone.emotional_range:
        lines.append(f"Emotional range: {', '.join(profile.tone.emotional_range)}")

    lines.append("\n--- BELIEFS ---")
    if profile.beliefs.core_values:
        lines.append(f"Core values: {', '.join(profile.beliefs.core_values)}")
    if profile.beliefs.stances:
        for topic, stance in profile.beliefs.stances.items():
            lines.append(f"Stance on {topic}: {stance}")

    lines.append("\n--- RED FLAGS (NEVER CROSS) ---")
    if profile.red_flags.trigger_topics:
        lines.append(f"Trigger topics: {', '.join(profile.red_flags.trigger_topics)}")
    if profile.red_flags.avoided_phrases:
        lines.append(f"Avoided phrases: {', '.join(profile.red_flags.avoided_phrases)}")

    return "\n".join(lines)
