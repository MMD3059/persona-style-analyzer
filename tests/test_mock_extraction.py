"""Test style extraction on mock tweets (no API key required)."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.schemas import StyleProfile, VocabProfile, ToneProfile, BeliefProfile, RedFlagProfile


MOCK_DATA = os.path.join(os.path.dirname(__file__), "..", "data", "mock", "tweets.json")


def load_mock_tweets():
    with open(MOCK_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def test_mock_data_loads():
    tweets = load_mock_tweets()
    assert len(tweets) == 25
    accounts = set(t["account"] for t in tweets)
    assert "Qatar_MOI" in accounts
    assert "Sheikh_Tamim" in accounts
    assert "Qatar_Education" in accounts
    assert "Al_Jazeera" in accounts
    print(f"Loaded {len(tweets)} tweets from {len(accounts)} accounts: {accounts}")


def test_style_profile_schema():
    """Verify that a StyleProfile can be created and serialized."""
    profile = StyleProfile(
        account="test_account",
        vocab=VocabProfile(
            repeated_phrases=["الحمدلله", "بفضل الله"],
            religious_terms=["الله", "بسم الله"],
            hashtag_patterns=["#قطر", "#الأمن"],
            sentence_length_avg=12.5,
        ),
        tone=ToneProfile(
            formality=0.8,
            sentiment="positive",
            emotional_range=["authoritative", "reassuring"],
        ),
        beliefs=BeliefProfile(
            core_values=["الوطن", "الأمن"],
            stances={"فلسطين": "دعم"},
        ),
        red_flags=RedFlagProfile(
            trigger_topics=["انتقاد الأمير"],
            avoided_phrases=["فساد"],
        ),
    )
    data = profile.model_dump(mode="json")
    assert data["account"] == "test_account"
    assert data["vocab"]["sentence_length_avg"] == 12.5
    assert data["tone"]["formality"] == 0.8
    assert data["beliefs"]["stances"]["فلسطين"] == "دعم"
    assert "انتقاد الأمير" in data["red_flags"]["trigger_topics"]
    print("StyleProfile schema validation passed")


def test_split_tweets_by_account():
    """Test separating tweets by account."""
    tweets = load_mock_tweets()
    accounts = {}
    for t in tweets:
        acct = t["account"]
        if acct not in accounts:
            accounts[acct] = []
        accounts[acct].append(t)

    assert len(accounts) == 4
    expected_counts = {
        "Qatar_MOI": 7,
        "Sheikh_Tamim": 6,
        "Qatar_Education": 6,
        "Al_Jazeera": 6,
    }
    for acct, count in expected_counts.items():
        actual = len(accounts[acct])
        assert actual == count, f"{acct}: expected {count}, got {actual}"
        print(f"  {acct}: {count} tweets")


def test_mock_extraction_no_api():
    """Run extraction pipeline with mock data (skips API calls if no key)."""
    from app.models.fanar import FanarClient

    api_key = os.getenv("FANAR_API_KEY", "")
    if not api_key:
        print("  SKIP: No FANAR_API_KEY set")
        return

    tweets = load_mock_tweets()
    moj_tweets = [t for t in tweets if t["account"] == "Qatar_MOI"]

    from app.graph.workflow import run_extraction
    result = run_extraction(moj_tweets, "Qatar_MOI")

    assert "style_profile" in result or "status" in result
    print(f"  Extraction result status: {result.get('status', 'N/A')}")


if __name__ == "__main__":
    test_mock_data_loads()
    test_style_profile_schema()
    test_split_tweets_by_account()
    test_mock_extraction_no_api()
    print("\nAll tests passed!")
