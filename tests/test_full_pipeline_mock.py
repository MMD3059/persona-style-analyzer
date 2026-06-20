"""Integration test: run full LangGraph pipeline with mocked FanarClient."""

import json
import os
import sys
from unittest.mock import patch

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MOCK_DATA = os.path.join(os.path.dirname(__file__), "..", "data", "mock", "tweets.json")


def load_mock_tweets():
    with open(MOCK_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def split_by_account(tweets):
    accounts = {}
    for t in tweets:
        acct = t["account"]
        if acct not in accounts:
            accounts[acct] = []
        accounts[acct].append(t)
    return accounts


MOCK_STYLE_PROFILES = {
    "Qatar_MOI": {
        "vocab": {
            "repeated_phrases": ["الحمدلله", "نعمل على مدار الساعة", "سلامتكم"],
            "religious_terms": ["الحمدلله", "بفضل الله"],
            "hashtag_patterns": ["#قطر", "#الأمن"],
            "unique_terms": ["وزارة الداخلية", "الأمن", "المواطنين"],
            "sentence_length_avg": 14.2,
            "formality_markers": ["تدعو", "نذكركم", "نعمل"],
        },
        "tone": {
            "formality": 0.85,
            "sentiment": "positive",
            "emotional_range": ["authoritative", "reassuring", "official"],
            "punctuation_style": "formal with periods",
            "emoji_usage": "none",
        },
        "beliefs": {
            "core_values": ["الوطن", "الأمن", "سلامة المواطن"],
            "stances": {"الأمن": "أولوية قصوى", "المواطن": "مسؤوليتنا"},
            "authority_references": ["القيادة الرشيدة", "وزارة الداخلية"],
            "in_group_vs_out_group": "نحن (الوزارة) → هم (المواطنون)",
        },
        "red_flags": {
            "trigger_topics": ["انتقاد الأجهزة الأمنية", "الإهمال الأمني"],
            "avoided_phrases": ["فشل", "اختراق", "انتهاك"],
            "typical_deflections": ["نعمل على مدار الساعة", "نحقق تقدم"],
            "sensitive_areas": ["أمن الدولة", "الجرائم الكبرى"],
        },
    },
    "Sheikh_Tamim": {
        "vocab": {
            "repeated_phrases": ["نفتخر", "قطر تمضي قدماً", "بفضل الله"],
            "religious_terms": ["الحمدلله", "بإذن الله"],
            "hashtag_patterns": ["#قطر_2030"],
            "unique_terms": ["الوطن", "الشعب", "المستقبل", "التنمية"],
            "sentence_length_avg": 10.8,
            "formality_markers": ["نؤكد", "نبارك", "نفتخر"],
        },
        "tone": {
            "formality": 0.75,
            "sentiment": "positive",
            "emotional_range": ["proud", "visionary", "warm"],
            "punctuation_style": "moderate, emotive",
            "emoji_usage": "none",
        },
        "beliefs": {
            "core_values": ["الوطن", "الشباب", "فلسطين", "الاستقلال"],
            "stances": {"فلسطين": "دعم ثابت", "التنمية": "التزام وطني"},
            "authority_references": ["الله", "الشعب الوفي"],
            "in_group_vs_out_group": "نحن (قطر) → هم (العالم)",
        },
        "red_flags": {
            "trigger_topics": ["التطبيع", "التنازل عن الحقوق"],
            "avoided_phrases": ["ضعف", "تراجع"],
            "typical_deflections": ["قطر تمضي قدماً", "نفتخر ببلدنا"],
            "sensitive_areas": ["السياسة الخارجية", "العلاقات الإقليمية"],
        },
    },
    "Qatar_Education": {
        "vocab": {
            "repeated_phrases": ["وزارة التربية والتعليم", "أبنائنا الطلاب", "التعليم"],
            "religious_terms": [],
            "hashtag_patterns": ["#التعليم", "#قطر_التعليم"],
            "unique_terms": ["منح دراسية", "مدرسة رقمية", "التفوق"],
            "sentence_length_avg": 13.5,
            "formality_markers": ["تعلن", "تهنئ", "تدعو"],
        },
        "tone": {
            "formality": 0.7,
            "sentiment": "positive",
            "emotional_range": ["encouraging", "formal", "celebratory"],
            "punctuation_style": "standard",
            "emoji_usage": "none",
        },
        "beliefs": {
            "core_values": ["العلم", "التفوق", "المستقبل"],
            "stances": {"التعليم": "أولوية وطنية", "التكنولوجيا": "أداة تطوير"},
            "authority_references": ["وزارة التربية", "المدارس"],
            "in_group_vs_out_group": "نحن (الوزارة) → هم (الطلاب)",
        },
        "red_flags": {
            "trigger_topics": ["تراجع التعليم", "فساد إداري"],
            "avoided_phrases": ["فشل", "تسرب"],
            "typical_deflections": ["التطوير مستمر", "نحن نعمل"],
            "sensitive_areas": ["المناهج", "نتائج الامتحانات"],
        },
    },
    "Al_Jazeera": {
        "vocab": {
            "repeated_phrases": ["عاجل", "مراسل الجزيرة", "مصادر مطلعة"],
            "religious_terms": [],
            "hashtag_patterns": [],
            "unique_terms": ["عاجل", "حصاد", "تحليل", "فيديو"],
            "sentence_length_avg": 8.2,
            "formality_markers": ["يصرح", "يكشف", "ينقل"],
        },
        "tone": {
            "formality": 0.55,
            "sentiment": "neutral",
            "emotional_range": ["urgent", "informative", "analytical"],
            "punctuation_style": "short, news-style",
            "emoji_usage": "none",
        },
        "beliefs": {
            "core_values": ["الخبر", "المصداقية", "التغطية"],
            "stances": {"غزة": "تغطية مستمرة", "فلسطين": "قضية مركزية"},
            "authority_references": ["مصادر", "مراسلون"],
            "in_group_vs_out_group": "نحن (الجزيرة) → هم (المتابعون)",
        },
        "red_flags": {
            "trigger_topics": ["الرقابة", "التعتيم الإعلامي"],
            "avoided_phrases": ["تحيز", "تزييف"],
            "typical_deflections": ["ننقل الخبر كما هو", "مصادر متعددة"],
            "sensitive_areas": ["الأمن القومي", "العلاقات الدبلوماسية"],
        },
    },
}

MOCK_EMBEDDINGS = {
    "Qatar_MOI": [0.9, 0.1, 0.3, 0.7, 0.2, 0.8, 0.4, 0.6, 0.5, 0.0],
    "Sheikh_Tamim": [0.8, 0.3, 0.5, 0.6, 0.9, 0.2, 0.7, 0.4, 0.1, 0.0],
    "Qatar_Education": [0.5, 0.7, 0.2, 0.4, 0.8, 0.3, 0.6, 0.1, 0.9, 0.0],
    "Al_Jazeera": [0.2, 0.9, 0.4, 0.3, 0.1, 0.7, 0.8, 0.5, 0.6, 0.0],
}

def mock_generate_structured(prompt, system_prompt=None, temperature=0.3):
    for account, profile in MOCK_STYLE_PROFILES.items():
        if account in prompt:
            return json.dumps(profile, ensure_ascii=False)
    return json.dumps(MOCK_STYLE_PROFILES["Qatar_MOI"], ensure_ascii=False)


def mock_embed(text):
    for account in MOCK_EMBEDDINGS:
        if account in text:
            return MOCK_EMBEDDINGS[account]
    return [0.0] * 10


def mock_generate(prompt, system_prompt=None, max_tokens=1500, temperature=0.3):
    return "نحن في وزارة الداخلية نعمل على مدار الساعة لخدمتكم وحماية أمنكم. الحمدلله على نعمة الأمان في وطننا الغالي قطر."


def apply_mocks():
    """Mock FanarClient at source BEFORE any agent modules import it."""
    p = patch("app.models.fanar.FanarClient")
    mock_cls = p.start()
    instance = mock_cls.return_value
    instance.generate_structured.side_effect = mock_generate_structured
    instance.generate.side_effect = mock_generate
    instance.embed.side_effect = mock_embed
    return [p]


def remove_mocks(patchers):
    for p in patchers:
        p.stop()


def test_pipeline_all_accounts():
    patchers = apply_mocks()
    try:
        tweets = load_mock_tweets()
        accounts = split_by_account(tweets)
        from app.graph.workflow import run_extraction

        results = {}
        for acct_name, acct_tweets in sorted(accounts.items()):
            result = run_extraction(acct_tweets, acct_name)
            results[acct_name] = result

            profile = result.get("style_profile")
            if isinstance(profile, dict):
                from app.models.schemas import StyleProfile
                profile = StyleProfile(**profile)

            print(f"\n{'='*50}")
            print(f"Account: {acct_name}")
            print(f"Tweets: {len(acct_tweets)}")
            print(f"Confidence: {result.get('extraction_confidence', 0):.2f}")
            print(f"Status: {result.get('status', 'completed')}")

            if profile:
                print(f"  Vocab: {len(profile.vocab.repeated_phrases)} repeated phrases, "
                      f"{len(profile.vocab.religious_terms)} religious terms")
                print(f"  Tone: formality={profile.tone.formality}, sentiment={profile.tone.sentiment}")
                print(f"  Beliefs: {len(profile.beliefs.core_values)} core values, "
                      f"{len(profile.beliefs.stances)} stances")
                print(f"  Red flags: {len(profile.red_flags.trigger_topics)} triggers, "
                      f"{len(profile.red_flags.avoided_phrases)} avoided phrases")

            assert profile is not None
            assert profile.account == acct_name

        print(f"\n{'='*50}")
        print(f"Pipeline ran successfully on {len(results)} accounts")
    finally:
        remove_mocks(patchers)
    return results


def test_verifier_node():
    import tempfile
    from app.db.faiss_index import FaissIndexManager
    from app.graph.workflow import run_verification
    import app.config as config_mod

    with tempfile.TemporaryDirectory() as tmpdir:
        test_account = "Qatar_MOI"
        # Override dimension to match mock embeddings (10-dim)
        import app.config as config_mod
        original_dim = config_mod.EMBEDDING_DIM
        config_mod.EMBEDDING_DIM = 10

        manager = FaissIndexManager(test_account, tmpdir, dim=10)
        emb = MOCK_EMBEDDINGS["Qatar_MOI"]
        texts = ["نحن في وزارة الداخلية نعمل لخدمتكم", "الحمدلله على نعمة الأمن"]
        manager.add(emb, texts[0])
        manager.add(emb, texts[1])
        manager.save()

        # Patch to use temp dir
        original = config_mod.INDICES_DIR
        config_mod.INDICES_DIR = tmpdir

        patchers = apply_mocks()
        try:
            result = run_verification(
                text="الحمدلله على نعمة الأمن والأمان في بلادنا الغالية قطر",
                account=test_account,
            )

            verification = result.get("verification", {})
            print(f"\nVerification for '{test_account}':")
            print(f"  Score: {verification.get('score', 0):.4f}")
            print(f"  Consistent: {verification.get('is_consistent', False)}")

            assert "score" in verification
            assert "is_consistent" in verification
        finally:
            remove_mocks(patchers)
            config_mod.INDICES_DIR = original
            config_mod.EMBEDDING_DIM = original_dim


def test_generator_node():
    from app.models.schemas import StyleProfile, VocabProfile, ToneProfile, BeliefProfile, RedFlagProfile
    from app.graph.workflow import run_generation

    profile = StyleProfile(
        account="Qatar_MOI",
        vocab=VocabProfile(**MOCK_STYLE_PROFILES["Qatar_MOI"]["vocab"]),
        tone=ToneProfile(**MOCK_STYLE_PROFILES["Qatar_MOI"]["tone"]),
        beliefs=BeliefProfile(**MOCK_STYLE_PROFILES["Qatar_MOI"]["beliefs"]),
        red_flags=RedFlagProfile(**MOCK_STYLE_PROFILES["Qatar_MOI"]["red_flags"]),
    )

    patchers = apply_mocks()
    try:
        result = run_generation(
            profile=profile,
            prompt="Write a tweet about community safety",
            account="Qatar_MOI",
            max_tokens=200,
        )

        text = result.get("generated_text", "")
        print(f"\nGenerated text for 'Qatar_MOI':")
        print(f"  {text[:100]}...")
        assert text
    finally:
        remove_mocks(patchers)


def test_build_faiss_indices():
    import tempfile
    from app.db.faiss_index import FaissIndexManager

    tweets = load_mock_tweets()
    accounts = split_by_account(tweets)

    with tempfile.TemporaryDirectory() as tmpdir:
        import app.config as config_mod
        original_dim = config_mod.EMBEDDING_DIM
        config_mod.EMBEDDING_DIM = 10

        try:
            indices = {}
            for acct_name, acct_tweets in sorted(accounts.items()):
                manager = FaissIndexManager(acct_name, tmpdir, dim=10)
                emb = MOCK_EMBEDDINGS.get(acct_name, [0.0] * 10)

                for t in acct_tweets:
                    manager.add(emb, t["content"])

                manager.save()
                assert os.path.exists(os.path.join(tmpdir, f"{acct_name}.faiss"))
                indices[acct_name] = manager
                print(f"  {acct_name}: FAISS index saved ({len(acct_tweets)} vectors)")

            # Query each index using raw embeddings (no FanarClient needed)
            for acct_name, manager in indices.items():
                query_emb = np.array([MOCK_EMBEDDINGS.get(acct_name, [0.0] * 10)], dtype=np.float32)
                distances, texts = manager.index.search(query_emb, k=2)
                print(f"  Query {acct_name}: dist={distances[0][0]:.4f}, text='{manager.metadata[0]['text'][:40]}...'")
                assert len(distances[0]) == 2

            print(f"Built {len(indices)} FAISS indices")
        finally:
            config_mod.EMBEDDING_DIM = original_dim


if __name__ == "__main__":
    print("=" * 60)
    print("FULL PIPELINE TEST (MOCKED)")
    print("=" * 60)

    print("\n--- Test 1: Extraction Pipeline on All Accounts ---")
    test_pipeline_all_accounts()

    print("\n--- Test 2: Verifier Node ---")
    test_verifier_node()

    print("\n--- Test 3: Generator Node ---")
    test_generator_node()

    print("\n--- Test 4: FAISS Index Building ---")
    test_build_faiss_indices()

    print("\n" + "=" * 60)
    print("ALL PIPELINE TESTS PASSED")
    print("=" * 60)
