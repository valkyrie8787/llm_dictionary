# dictionary_project/lang_plugins/en_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import EnglishFeatures, ValueField, Provenance, PosType
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)

class RawEnglishData(BaseModel):
    word: str
    source: str = "wordnet_3.0"
    pos: Optional[str] = None
    examples: List[str] = []
    confidence_map: Dict[str, float] = {}
    prompt_id: Optional[str] = None
    generated_by: str = "rule_based"

def _create_value_field(value: Optional[str], key: str, provenance: Provenance, conf_map: Dict) -> Optional[ValueField]:
    if value is not None:
        confidence = conf_map.get(key, conf_map.get("default", 0.99))
        return ValueField(value=value, provenance=provenance, confidence=confidence)
    logging.debug(f"Missing '{key}' in raw_data")
    return None

def parse_english_data(raw_data: RawEnglishData) -> EnglishFeatures:
    provenance = Provenance(
        source=raw_data.source,
        prompt_id=raw_data.prompt_id,
        generated_by=raw_data.generated_by
    )
    word_target_vf = ValueField(value=raw_data.word, provenance=provenance, confidence=raw_data.confidence_map.get("word", 1.0))
    part_of_speech_vf = _create_value_field(raw_data.pos, "pos", provenance, raw_data.confidence_map)
    examples = [_create_value_field(ex, "examples", provenance, raw_data.confidence_map) for ex in raw_data.examples] if raw_data.examples else []

    return EnglishFeatures(
        word_target=word_target_vf,
        part_of_speech=part_of_speech_vf,
        examples=examples
    )