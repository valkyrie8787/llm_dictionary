# dictionary_project/lang_plugins/fr_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import FrenchFeatures, ValueField, Provenance, Inflection, PosType
from utils.confidence import assign_confidence
from utils.helpers import create_value_field, map_pos_tag
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)

class RawFrenchData(BaseModel):
    word: str
    source: str = "gpt-oss:20b"
    pos: Optional[str] = None
    gender: Optional[str] = None
    number: Optional[str] = None
    verb_tenses: Dict[str, str] = {}
    examples: List[str] = []
    confidence_map: Dict[str, float] = {}
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"
    definition_target: Optional[str] = None
    example_target: Optional[str] = None

async def parse_french_data(raw_data: RawFrenchData) -> FrenchFeatures:
    provenance = Provenance(
        source=raw_data.source,
        prompt_id=raw_data.prompt_id,
        generated_by=raw_data.generated_by
    )
    confidence_map = raw_data.confidence_map or {
        "word": assign_confidence(raw_data.source, "word"),
        "pos": assign_confidence(raw_data.source, "pos"),
        "gender": assign_confidence(raw_data.source, "gender"),
        "number": assign_confidence(raw_data.source, "number"),
        "examples": assign_confidence(raw_data.source, "examples"),
        "definition_target": assign_confidence(raw_data.source, "definition_target")
    }
    standard_pos = map_pos_tag(raw_data.pos, "fr")
    word_target_vf = ValueField(
        value=raw_data.word,
        provenance=provenance,
        confidence=confidence_map.get("word", assign_confidence(raw_data.source, "word"))
    )
    gender_vf = await create_value_field(raw_data.gender, "gender", provenance, confidence_map)
    number_vf = await create_value_field(raw_data.number, "number", provenance, confidence_map)
    part_of_speech_vf = await create_value_field(
        standard_pos.value if standard_pos else None, "pos", provenance, confidence_map
    )
    verb_tenses = [
        Inflection(form=await create_value_field(form, tense, provenance, confidence_map), type=tense)
        async for tense, form in raw_data.verb_tenses.items()
    ] if raw_data.verb_tenses else []
    examples = [
        await create_value_field(raw_data.example_target or ex, "examples", provenance, confidence_map)
        async for ex in raw_data.examples
    ] if raw_data.example_target or raw_data.examples else []

    return FrenchFeatures(
        word_target=word_target_vf,
        part_of_speech=part_of_speech_vf,
        gender=gender_vf,
        number=number_vf,
        verb_tenses=verb_tenses,
        examples=examples
    )