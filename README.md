# Persona Style Analyzer

Extract, verify, and generate Arabic social media communication style profiles using Fanar LLM.

## Architecture

```
Twitter Data
    ↓
┌────────────────────────────────────────────────┐
│              LangGraph Pipeline               │
│                                                │
│  StyleExtractor → Verifier → Generator → Output │
│                                                │
│  - StyleExtractor: tweets → Fanar → style JSON │
│  - Verifier:       text + FAISS → match score  │
│  - Generator:      profile + prompt → new text  │
│  - Output:         save + format results        │
└────────────────────────────────────────────────┘
    ↓
StyleProfile JSON  ──  FAISS Index  ──  FastAPI
(per account)           (per account)       (REST)
```

## Style Profile Schema

Each account's style is extracted into a JSON with 4 dimensions:

- **vocab**: repeated_phrases, religious_terms, hashtags, formality markers
- **tone**: formality (0-1), sentiment, emotional range, punctuation
- **beliefs**: core values, stances, authority references, in/out-group
- **red_flags**: trigger topics, avoided phrases, deflections, sensitive areas

This mirrors the pattern from persona-hub/chat_with_me style extraction.

## Setup

```bash
# 1. Clone
git clone https://github.com/your-org/persona-style-analyzer.git
cd persona-style-analyzer

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env → set your FANAR_API_KEY

# 4. Run
uvicorn app.main:app --reload
```

## API Endpoints

### `POST /extract`

Extract a style profile from an account's tweets.

```json
{
  "account": "Qatar_MOI",
  "tweets": [
    {"content": "الحمدلله على نعمة الأمن والأمان في بلادنا الغالية قطر"}
  ]
}
```

### `POST /verify`

Check if text matches an account's style.

```json
{
  "account": "Qatar_MOI",
  "text": "نحن في وزارة الداخلية نعمل لخدمتكم"
}
```

### `POST /generate`

Generate text in an account's extracted style.

```json
{
  "account": "Qatar_MOI",
  "prompt": "Write a tweet about traffic safety"
}
```

## Project Structure

```
persona-style-analyzer/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Env-based configuration
│   ├── models/
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── fanar.py         # Fanar API client (OpenAI-compatible)
│   ├── agents/
│   │   ├── extractor.py     # StyleExtractor LangGraph node
│   │   ├── verifier.py      # Verifier LangGraph node
│   │   ├── generator.py     # Generator LangGraph node
│   │   └── output.py        # Output LangGraph node
│   ├── graph/
│   │   └── workflow.py      # LangGraph state machine
│   ├── db/
│   │   └── faiss_index.py   # FAISS vector index per account
│   ├── utils/
│   │   └── embeddings.py    # Embedding + index building
│   └── data/
│       ├── mock/tweets.json # Mock Arabic tweets for testing
│       ├── profiles/        # Extracted style profiles (output)
│       ├── indices/         # FAISS indices (output)
│       └── raw/             # Raw incoming tweet data
├── tests/
│   └── test_mock_extraction.py
├── .env.example
├── requirements.txt
└── README.md
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI |
| LLM | Fanar (OpenAI-compatible via QCRI/HBKU) |
| Orchestration | LangGraph |
| Vector Search | FAISS (one index per account) |
| Validation | Pydantic v2 |
