from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime


class Tweet(BaseModel):
    id: str
    account: str
    content: str
    created_at: Optional[datetime] = None
    likes: Optional[int] = 0
    retweets: Optional[int] = 0


class VocabProfile(BaseModel):
    repeated_phrases: list[str] = Field(default_factory=list)
    religious_terms: list[str] = Field(default_factory=list)
    hashtag_patterns: list[str] = Field(default_factory=list)
    unique_terms: list[str] = Field(default_factory=list)
    sentence_length_avg: Optional[float] = None
    formality_markers: list[str] = Field(default_factory=list)


class ToneProfile(BaseModel):
    formality: float = Field(default=0.5, ge=0.0, le=1.0)
    sentiment: str = "neutral"
    emotional_range: list[str] = Field(default_factory=list)
    punctuation_style: Any = None
    emoji_usage: Any = None


class BeliefProfile(BaseModel):
    core_values: list[str] = Field(default_factory=list)
    stances: dict[str, str] = Field(default_factory=dict)
    authority_references: list[str] = Field(default_factory=list)
    in_group_vs_out_group: Optional[str] = None


class RedFlagProfile(BaseModel):
    trigger_topics: list[str] = Field(default_factory=list)
    avoided_phrases: list[str] = Field(default_factory=list)
    typical_deflections: list[str] = Field(default_factory=list)
    sensitive_areas: list[str] = Field(default_factory=list)


class StyleProfile(BaseModel):
    """Style profile extracted from an account's tweets."""

    account: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

    # Vocabulary & phrasing
    vocab: VocabProfile = Field(default_factory=lambda: VocabProfile())
    # Tone & emotion
    tone: ToneProfile = Field(default_factory=lambda: ToneProfile())
    # Beliefs & values
    beliefs: BeliefProfile = Field(default_factory=lambda: BeliefProfile())
    # Red flags & boundaries
    red_flags: RedFlagProfile = Field(default_factory=lambda: RedFlagProfile())

    created_at: datetime = Field(default_factory=datetime.now)
    model: str = "Fanar-C-2-27B"

    class Config:
        json_schema_extra = {
            "example": {
                "account": "Qatar_MOI",
                "vocab": {"repeated_phrases": ["الأمن أولاً", "سلامة الوطن"],
                          "religious_terms": ["الحمدلله", "بفضل الله"],
                          "hashtag_patterns": ["#قطر", "#الأمن"]},
                "tone": {"formality": 0.8, "sentiment": "positive",
                          "emotional_range": ["authoritative", "reassuring"]},
                "beliefs": {"core_values": ["الوطن", "الأمن", "الاستقرار"],
                            "stances": {"قضية فلسطين": "دعم مطلق"}},
                "red_flags": {"trigger_topics": ["انتقاد الأمير"],
                              "avoided_phrases": ["فساد", "انتهاكات"]}
            }
        }


class ExtractionRequest(BaseModel):
    tweets: list[Tweet]
    account: str
    full_name: Optional[str] = None
    bio: Optional[str] = None


class ExtractionResponse(BaseModel):
    profile: StyleProfile
    confidence: float
    tweet_count: int


class VerificationRequest(BaseModel):
    text: str
    account: str


class VerificationResponse(BaseModel):
    account: str
    similarity_score: float
    is_consistent: bool
    details: dict = Field(default_factory=dict)


class GenerationRequest(BaseModel):
    account: str
    prompt: str
    max_tokens: int = 500


class GenerationResponse(BaseModel):
    text: str
    account: str
    style_adherence: float
