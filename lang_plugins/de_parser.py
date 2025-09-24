# dictionary_project/lang_plugins/de_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import GermanFeatures, Inflection, Provenance
from utils.helpers import create_value_field, map_pos_tag
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

class RawGermanData(BaseModel):
    word: str
    source: str
    pos: Optional[str] = None
    gender: Optional[str] = None
    plural: Optional[str] = None
    declensions: Dict[str, str] = {}
    examples: List[str] = []
    definition_target: Optional[str] = None
    example_target: Optional[str] = None
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"
    source_licenses: Optional[Dict[str, str]] = None

async def parse_german_data(raw_data: RawGermanData) -> GermanFeatures:
    if not raw_data.word:
        raise ValueError("Field 'word' cannot be empty.")
    provenance = Provenance(source=raw_data.source, prompt_id=raw_data.prompt_id, generated_by=raw_data.generated_by)
    standard_pos = map_pos_tag(raw_data.pos, "de")
    all_examples = raw_data.examples[:]
    if raw_data.example_target:
        all_examples.append(raw_data.example_target)

    return GermanFeatures(
        word_target=await create_value_field(raw_data.word, "word", provenance, lang="de"),
        part_of_speech=await create_value_field(standard_pos.value if standard_pos else None, "pos", provenance, lang="de"),
        definition=await create_value_field(raw_data.definition_target, "definition", provenance, lang="de"),
        gender=await create_value_field(raw_data.gender, "gender", provenance, lang="de"),
        plural=await create_value_field(raw_data.plural, "plural", provenance, lang="de"),
        declension_table=[
            Inflection(form=await create_value_field(form, case, provenance, lang="de"), type=case)
            async for case, form in raw_data.declensions.items()
        ],
        examples=[
            await create_value_field(ex, "examples", provenance, lang="de")
            async for ex in all_examples
        ]
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    async def main():
        sample_data = RawGermanData(
            word="Tisch",
            source="omw_v1",
            pos="Substantiv",
            gender="m",
            plural="Tische",
            definition_target="Ein Möbelstück mit einer flachen Platte.",
            source_licenses={"omw": "Princeton License"}
        )
        try:
            parsed = await parse_german_data(sample_data)
            print("--- German Parser Test ---")
            print(parsed.json(indent=2, ensure_ascii=False))
        except ValueError as e:
            logger.error(f"Parsing error: {e}")

        error_cases = [
            RawGermanData(word="", source="omw_v1"),
            RawGermanData(word="Tisch", source="omw_v1", pos="wrongpos")
        ]
        for case in error_cases:
            try:
                print(f"\n--- Error Case: {case} ---")
                parsed = await parse_german_data(case)
                print(parsed.json(indent=2))
            except ValueError as e:
                logger.warning(f"Test case failed: {e}")

        json_path = Path("dict_de_2letter.json")
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            for entry in json_data[:2]:
                try:
                    raw = RawGermanData(**entry)
                    parsed = await parse_german_data(raw)
                    print(f"\n--- JSON Test: {raw.word} ---")
                    print(parsed.json(indent=2, ensure_ascii=False))
                except ValueError as e:
                    logger.warning(f"JSON test failed for {entry.get('word', 'unknown')}: {e}")

    asyncio.run(main())