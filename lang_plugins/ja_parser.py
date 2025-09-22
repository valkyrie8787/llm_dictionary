# dictionary_project/lang_plugins/ja_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import JapaneseFeatures, ValueField, Provenance, Inflection, PosType
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)

class RawJapaneseData(BaseModel):
    word: str
    source: str = "omw_v1_japanese"
    pos: Optional[str] = None
    kanji: Optional[str] = None
    hiragana: Optional[str] = None
    katakana: Optional[str] = None
    romanization: Optional[str] = None
    politeness_levels: Dict[str, str] = {}
    examples: List[str] = []
    confidence_map: Dict[str, float] = {}
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"

def _create_value_field(value: Optional[str], key: str, provenance: Provenance, conf_map: Dict) -> Optional[ValueField]:
    if value is not None:
        confidence = conf_map.get(key, conf_map.get("default", 0.95))
        return ValueField(value=value, provenance=provenance, confidence=confidence)
    logging.debug(f"Missing '{key}' in raw_data")
    return None

def parse_japanese_data(raw_data: RawJapaneseData) -> JapaneseFeatures:
    provenance = Provenance(
        source=raw_data.source,
        prompt_id=raw_data.prompt_id,
        generated_by=raw_data.generated_by
    )
    word_target_vf = ValueField(value=raw_data.word, provenance=provenance, confidence=raw_data.confidence_map.get("word", 0.98))
    kanji_vf = _create_value_field(raw_data.kanji, "kanji", provenance, raw_data.confidence_map)
    hiragana_vf = _create_value_field(raw_data.hiragana, "hiragana", provenance, raw_data.confidence_map)
    katakana_vf = _create_value_field(raw_data.katakana, "katakana", provenance, raw_data.confidence_map)
    romanization_vf = _create_value_field(raw_data.romanization, "romanization", provenance, raw_data.confidence_map)
    part_of_speech_vf = _create_value_field(raw_data.pos, "pos", provenance, raw_data.confidence_map)
    politeness_levels = [Inflection(form=_create_value_field(form, p_level, provenance, raw_data.confidence_map), type=p_level) for p_level, form in raw_data.politeness_levels.items()] if raw_data.politeness_levels else []
    examples = [_create_value_field(ex, "examples", provenance, raw_data.confidence_map) for ex in raw_data.examples] if raw_data.examples else []

    return JapaneseFeatures(
        word_target=word_target_vf,
        part_of_speech=part_of_speech_vf,
        kanji=kanji_vf,
        hiragana=hiragana_vf,
        katakana=katakana_vf,
        romanization=romanization_vf,
        politeness_levels=politeness_levels,
        examples=examples
    )