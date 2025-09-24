# dictionary_project/lang_plugins/es_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import SpanishFeatures, Inflection, Provenance
from utils.helpers import create_value_field, map_pos_tag
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

class RawSpanishData(BaseModel):
    word: str
    source: str
    pos: Optional[str] = None
    gender: Optional[str] = None
    number: Optional[str] = None
    verb_conjugations: Dict[str, str] = {}
    examples: List[str] = []
    definition_target: Optional[str] = None
    example_target: Optional[str] = None
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"
    source_licenses: Optional[Dict[str, str]] = None

async def parse_spanish_data(raw_data: RawSpanishData) -> SpanishFeatures:
    if not raw_data.word:
        raise ValueError("Field 'word' cannot be empty.")
    provenance = Provenance(source=raw_data.source, prompt_id=raw_data.prompt_id, generated_by=raw_data.generated_by)
    standard_pos = map_pos_tag(raw_data.pos, "es")
    all_examples = raw_data.examples[:]
    if raw_data.example_target:
        all_examples.append(raw_data.example_target)

    return SpanishFeatures(
        word_target=await create_value_field(raw_data.word, "word", provenance, lang="es"),
        part_of_speech=await create_value_field(standard_pos.value if standard_pos else None, "pos", provenance, lang="es"),
        definition=await create_value_field(raw_data.definition_target, "definition", provenance, lang="es"),
        gender=await create_value_field(raw_data.gender, "gender", provenance, lang="es"),
        number=await create_value_field(raw_data.number, "number", provenance, lang="es"),
        verb_conjugations=[
            Inflection(form=await create_value_field(form, tense, provenance, lang="es"), type=tense)
            async for tense, form in raw_data.verb_conjugations.items()
        ],
        examples=[
            await create_value_field(ex, "examples", provenance, lang="es")
            async for ex in all_examples
        ]
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    async def main():
        sample_data = RawSpanishData(
            word="mesa",
            source="omw_v1",
            pos="nombre",
            gender="f",
            definition_target="Mueble compuesto de un tablero horizontal liso.",
            source_licenses={"omw": "Princeton License"}
        )
        try:
            parsed = await parse_spanish_data(sample_data)
            print("--- Spanish Parser Test ---")
            print(parsed.json(indent=2, ensure_ascii=False))
        except ValueError as e:
            logger.error(f"Parsing error: {e}")

        error_cases = [
            RawSpanishData(word="", source="omw_v1"),
            RawSpanishData(word="mesa", source="omw_v1", pos="wrongpos")
        ]
        for case in error_cases:
            try:
                print(f"\n--- Error Case: {case} ---")
                parsed = await parse_spanish_data(case)
                print(parsed.json(indent=2))
            except ValueError as e:
                logger.warning(f"Test case failed: {e}")

        json_path = Path("dict_es_2letter.json")
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            for entry in json_data[:2]:
                try:
                    raw = RawSpanishData(**entry)
                    parsed = await parse_spanish_data(raw)
                    print(f"\n--- JSON Test: {raw.word} ---")
                    print(parsed.json(indent=2, ensure_ascii=False))
                except ValueError as e:
                    logger.warning(f"JSON test failed for {entry.get('word', 'unknown')}: {e}")

    asyncio.run(main())