# dictionary_project/lang_plugins/ko_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import KoreanFeatures, ValueField, Provenance, Inflection
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)

class RawKoreanData(BaseModel):
    word: str
    source: str = "gpt-oss:20b"
    pos: Optional[str] = None
    hanja: Optional[str] = None
    romanization: Optional[str] = None
    conjugations: Dict[str, str] = {}
    examples: List[str] = []
    confidence_map: Dict[str, float] = {}
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"
    definition_target: Optional[str] = None
    example_target: Optional[str] = None

def _create_value_field(value: Optional[str], key: str, provenance: Provenance, conf_map: Dict) -> Optional[ValueField]:
    if value is not None:
        confidence = conf_map.get(key, conf_map.get("default", 0.95))
        return ValueField(value=value, provenance=provenance, confidence=confidence)
    logging.warning(f"Missing '{key}' in raw_data")
    return None

def parse_korean_data(raw_data: RawKoreanData) -> KoreanFeatures:
    provenance = Provenance(
        source=raw_data.source,
        prompt_id=raw_data.prompt_id,
        generated_by=raw_data.generated_by
    )
    confidence_map = raw_data.confidence_map or {
        "word": raw_data.confidence_map.get("word", 0.8),
        "pos": 0.95,
        "examples": 0.85,
        "definition_target": 0.85
    }
    examples = [
        _create_value_field(raw_data.example_target or ex, "examples", provenance, confidence_map)
        for ex in raw_data.examples
    ] if raw_data.example_target or raw_data.examples else None
    return KoreanFeatures(
        word_target=ValueField(value=raw_data.word, provenance=provenance, confidence=confidence_map.get("word", 0.8)),
        hanja=_create_value_field(raw_data.hanja, "hanja", provenance, confidence_map),
        romanization=_create_value_field(raw_data.romanization, "romanization", provenance, confidence_map),
        part_of_speech=_create_value_field(raw_data.pos, "pos", provenance, confidence_map),
        conjugation_samples=[
            Inflection(form=_create_value_field(form, conj_type, provenance, confidence_map), type=conj_type)
            for conj_type, form in raw_data.conjugations.items()
        ] if raw_data.conjugations else None,
        examples=examples
    )