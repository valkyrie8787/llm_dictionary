# dictionary_project/lang_plugins/hr_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import CroatianFeatures, ValueField, Provenance, Inflection, PosType
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)

class RawCroatianData(BaseModel):
    word: str
    source: str = "omw_v1_croatian"
    pos: Optional[str] = None
    gender: Optional[str] = None
    aspect: Optional[str] = None
    declensions: Dict[str, str] = {}
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

def parse_croatian_data(raw_data: RawCroatianData) -> CroatianFeatures:
    provenance = Provenance(
        source=raw_data.source,
        prompt_id=raw_data.prompt_id,
        generated_by=raw_data.generated_by
    )
    word_target_vf = ValueField(value=raw_data.word, provenance=provenance, confidence=raw_data.confidence_map.get("word", 0.98))
    gender_vf = _create_value_field(raw_data.gender, "gender", provenance, raw_data.confidence_map)
    aspect_vf = _create_value_field(raw_data.aspect, "aspect", provenance, raw_data.confidence_map)
    part_of_speech_vf = _create_value_field(raw_data.pos, "pos", provenance, raw_data.confidence_map)
    declensions = [Inflection(form=_create_value_field(form, case, provenance, raw_data.confidence_map), type=case) for case, form in raw_data.declensions.items()] if raw_data.declensions else []
    examples = [_create_value_field(ex, "examples", provenance, raw_data.confidence_map) for ex in raw_data.examples] if raw_data.examples else []

    return CroatianFeatures(
        word_target=word_target_vf,
        part_of_speech=part_of_speech_vf,
        gender=gender_vf,
        declensions=declensions,
        aspect=aspect_vf,
        examples=examples
    )