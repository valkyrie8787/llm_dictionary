# dictionary_project/lang_plugins/zh_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import ChineseFeatures, ValueField, Provenance, Inflection, PosType
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)

class RawChineseData(BaseModel):
    word: str
    source: str = "omw_v1_chinese"
    pos: Optional[str] = None
    simplified: Optional[str] = None
    traditional: Optional[str] = None
    pinyin: Optional[str] = None
    tones: Optional[str] = None
    measure_words: Dict[str, str] = {}
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

def parse_chinese_data(raw_data: RawChineseData) -> ChineseFeatures:
    provenance = Provenance(
        source=raw_data.source,
        prompt_id=raw_data.prompt_id,
        generated_by=raw_data.generated_by
    )
    word_target_vf = ValueField(value=raw_data.word, provenance=provenance, confidence=raw_data.confidence_map.get("word", 0.98))
    simplified_vf = _create_value_field(raw_data.simplified, "simplified", provenance, raw_data.confidence_map)
    traditional_vf = _create_value_field(raw_data.traditional, "traditional", provenance, raw_data.confidence_map)
    pinyin_vf = _create_value_field(raw_data.pinyin, "pinyin", provenance, raw_data.confidence_map)
    tones_vf = _create_value_field(raw_data.tones, "tones", provenance, raw_data.confidence_map)
    part_of_speech_vf = _create_value_field(raw_data.pos, "pos", provenance, raw_data.confidence_map)
    measure_words = [Inflection(form=_create_value_field(form, m_word, provenance, raw_data.confidence_map), type=m_word) for m_word, form in raw_data.measure_words.items()] if raw_data.measure_words else []
    examples = [_create_value_field(ex, "examples", provenance, raw_data.confidence_map) for ex in raw_data.examples] if raw_data.examples else []

    return ChineseFeatures(
        word_target=word_target_vf,
        part_of_speech=part_of_speech_vf,
        simplified=simplified_vf,
        traditional=traditional_vf,
        pinyin=pinyin_vf,
        tones=tones_vf,
        measure_words=measure_words,
        examples=examples
    )