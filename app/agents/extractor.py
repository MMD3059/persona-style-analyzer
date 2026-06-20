"""StyleExtractor Agent.

Takes an account's tweets, sends them to Fanar,
and extracts a structured StyleProfile JSON.
"""

import json
from app.models.schemas import StyleProfile, VocabProfile, ToneProfile, BeliefProfile, RedFlagProfile
from app.models.fanar import FanarClient

EXTRACTOR_SYSTEM_PROMPT = """You are a professional linguistic and behavioral analyst specializing in Arabic-language style extraction. Your task is to analyze a set of tweets from a specific account and extract their communication style into a structured JSON profile.

Focus on:
1. VOCABULARY & PHRASING: Repeated phrases, religious terms, hashtag patterns, unique terms, average sentence length, formality markers.
2. TONE & EMOTION: Formality level (0.0-1.0), overall sentiment, emotional range, punctuation style, emoji usage.
3. BELIEFS & VALUES: Core values repeated themes, stances on key topics, authority references, in-group vs out-group language.
4. RED FLAGS: Topics that trigger strong reactions, avoided phrases, typical deflection patterns, sensitive areas.

Return ONLY valid JSON matching this schema (no markdown, no explanation):
{
  "vocab": {
    "repeated_phrases": [],
    "religious_terms": [],
    "hashtag_patterns": [],
    "unique_terms": [],
    "sentence_length_avg": null,
    "formality_markers": []
  },
  "tone": {
    "formality": 0.5,
    "sentiment": "neutral",
    "emotional_range": [],
    "punctuation_style": null,
    "emoji_usage": null
  },
  "beliefs": {
    "core_values": [],
    "stances": {},
    "authority_references": [],
    "in_group_vs_out_group": null
  },
  "red_flags": {
    "trigger_topics": [],
    "avoided_phrases": [],
    "typical_deflections": [],
    "sensitive_areas": []
  }
}"""


def style_extractor_node(state: dict) -> dict:
    """
    LangGraph node: takes tweets from state, calls Fanar,
    returns StyleProfile.
    """
    tweets = state.get("tweets", [])
    account = state.get("account", "unknown")
    fanar = FanarClient()

    # Build prompt from tweets
    tweet_texts = []
    for t in tweets[:50]:  # limit to 50 tweets per extraction
        content = t.get("content", t.content if hasattr(t, "content") else str(t))
        tweet_texts.append(f"- {content}")

    tweets_block = "\n".join(tweet_texts)

    prompt = (
        f"Analyze the following tweets from the account '{account}' "
        f"and extract their communication style profile.\n\n"
        f"TWEETS:\n{tweets_block}\n\n"
        f"Return the JSON profile as specified."
    )

    try:
        response = fanar.generate_structured(
            prompt=prompt,
            system_prompt=EXTRACTOR_SYSTEM_PROMPT,
        )
        # Clean response - remove markdown fences if present
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1]
            response = response.rsplit("```", 1)[0]
        response = response.strip()

        profile_data = json.loads(response)
        profile = StyleProfile(
            account=account,
            vocab=VocabProfile(**profile_data.get("vocab", {})),
            tone=ToneProfile(**profile_data.get("tone", {})),
            beliefs=BeliefProfile(**profile_data.get("beliefs", {})),
            red_flags=RedFlagProfile(**profile_data.get("red_flags", {})),
        )

    except (json.JSONDecodeError, Exception) as e:
        # Fallback: return empty profile on error
        profile = StyleProfile(account=account)

    return {
        **state,
        "style_profile": profile,
        "extraction_confidence": _calculate_confidence(profile, len(tweets)),
    }


def _calculate_confidence(profile: StyleProfile, tweet_count: int) -> float:
    """Calculate confidence score based on extraction completeness."""
    confidence = 0.3  # base
    if len(profile.vocab.repeated_phrases) > 0:
        confidence += 0.15
    if profile.tone.sentiment != "neutral":
        confidence += 0.15
    if len(profile.beliefs.core_values) > 0:
        confidence += 0.15
    if len(profile.red_flags.trigger_topics) > 0:
        confidence += 0.1
    if tweet_count >= 10:
        confidence += 0.15
    return min(confidence, 1.0)
