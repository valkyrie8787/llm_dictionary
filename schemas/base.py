# dictionary_project/schemas/base.py (v1.4, Refactored with Inheritance + Fixes)
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
from pydantic import Field

class DictionaryRoot(BaseModel):
    word_en: str = Field(..., min_length=1, max_length=80)

class PosType(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJ = "adjective"
    ADV = "adverb"
    OTHER = "other"

# --- 1. ✅ Provenance 확장: timestamp와 annotator_id 추가 ---
class Provenance(BaseModel):
    """Tracks the origin and metadata of a single piece of linguistic data."""
    source: str = Field(..., description="Source of the data (e.g., 'omw_v1', 'llm:gpt-oss-120b').")
    generated_by: str = "gpt-oss-120b-v1.0"
    prompt_id: Optional[str] = Field(None, description="ID of the prompt template used.")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Timestamp of data creation (UTC ISO 8601).")
    annotator_id: Optional[str] = Field(None, description="ID of the human annotator if manually verified.")

class ValueField(BaseModel):
    """Holds a value with its provenance and confidence."""
    value: Any
    provenance: Provenance
    confidence: float

    @validator('confidence')
    def confidence_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

class Inflection(BaseModel):
    form: ValueField
    type: str
    # ✅ 확장 가능성 고려: 시제, 상, 태, 서법 등
    tense: Optional[str] = None
    aspect: Optional[str] = None
    mood: Optional[str] = None

# --- 2. ✅ BaseFeatures 상속 구조 도입 ---
class BaseFeatures(BaseModel):
    """Base class for linguistic features common to all languages."""
    word_target: ValueField
    part_of_speech: Optional[ValueField] = None
    examples: List[ValueField] = Field(default_factory=list)

# --- 3. 언어별 Features 클래스 ---
class EnglishFeatures(BaseFeatures):
    pass

class GermanFeatures(BaseFeatures):
    gender: Optional[ValueField] = None
    plural: Optional[ValueField] = None
    declension_table: List[Inflection] = Field(default_factory=list)

class CroatianFeatures(BaseFeatures):
    gender: Optional[ValueField] = None
    declensions: List[Inflection] = Field(default_factory=list)
    aspect: Optional[ValueField] = None

class KoreanFeatures(BaseFeatures):
    hanja: Optional[ValueField] = None
    romanization: Optional[ValueField] = None
    conjugation_samples: List[Inflection] = Field(default_factory=list)

class SpanishFeatures(BaseFeatures):
    gender: Optional[ValueField] = None
    number: Optional[ValueField] = None
    verb_conjugations: List[Inflection] = Field(default_factory=list)

class FrenchFeatures(BaseFeatures):
    gender: Optional[ValueField] = None
    number: Optional[ValueField] = None
    verb_tenses: List[Inflection] = Field(default_factory=list)

class JapaneseFeatures(BaseFeatures):
    kanji: Optional[ValueField] = None
    hiragana: Optional[ValueField] = None
    katakana: Optional[ValueField] = None
    romanization: Optional[ValueField] = None
    politeness_levels: List[Inflection] = Field(default_factory=list)

class ChineseFeatures(BaseFeatures):
    simplified: Optional[ValueField] = None
    traditional: Optional[ValueField] = None
    pinyin: Optional[ValueField] = None
    tones: Optional[ValueField] = None
    measure_words: List[Inflection] = Field(default_factory=list)

class Sense(BaseModel):
    """Represents a single sense (meaning) of an English word, aligned with WordNet."""
    sense_id: str
    definition_en: str
    examples_en: List[str] = Field(default_factory=list) # ✅ WordNet 예문
    translations: Dict[str, BaseFeatures] # ✅ 단순화: 모든 언어는 BaseFeatures 상속

class DictionaryRoot(BaseModel):
    """The root model for a dictionary entry file."""
    schema_version: str = "1.4"  # ✅ 업데이트: 상속 구조 + Provenance 확장 + List 안전화 반영
    word_en: str = Field(..., min_length=1, max_length=80, description="The headword in English.")
    senses: List[Sense] = Field(default_factory=list)
