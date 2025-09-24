# dictionary_project/lang_plugins/hr_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import CroatianFeatures, Inflection, Provenance
from utils.helpers import create_value_field, map_pos_tag
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

class RawCroatianData(BaseModel):
    word: str
    source: str
    pos: Optional[str] = None
    gender: Optional[str] = None
    declensions: Dict[str, str] = {}
    aspect: Optional[str] = None
    examples: List[str] = []
    definition_target: Optional[str] = None
    example_target: Optional[str] = None
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"
    source_licenses: Optional[Dict[str, str]] = None

async def parse_croatian_data(raw_data: RawCroatianData) -> CroatianFeatures:
    if not raw_data.word:
        raise ValueError("Field 'word' cannot be empty.")
    provenance = Provenance(source=raw_data.source, prompt_id=raw_data.prompt_id, generated_by=raw_data.generated_by)
    standard_pos = map_pos_tag(raw_data.pos, "hr")
    all_examples = raw_data.examples[:]
    if raw_data.example_target:
        all_examples.append(raw_data.example_target)

    return CroatianFeatures(
        word_target=await create_value_field(raw_data.word, "word", provenance, lang="hr"),
        part_of_speech=await create_value_field(standard_pos.value if standard_pos else None, "pos", provenance, lang="hr"),
        definition=await create_value_field(raw_data.definition_target, "definition", provenance, lang="hr"),
        gender=await create_value_field(raw_data.gender, "gender", provenance, lang="hr"),
        declensions=[
            Inflection(form=await create_value_field(form, case, provenance, lang="hr"), type=case)
            async for case, form in raw_data.declensions.items()
        ],
        aspect=await create_value_field(raw_data.aspect, "aspect", provenance, lang="hr"),
        examples=[
            await create_value_field(ex, "examples", provenance, lang="hr")
            async for ex in all_examples
        ]
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    async def main():
        sample_data = RawCroatianData(
            word="stol",
            source="omw_v1",
            pos="imenica",
            gender="m",
            definition_target="Komad namještaja s ravnom pločom.",
            source_licenses={"omw": "Princeton License"}
        )
        try:
            parsed = await parse_croatian_data(sample_data)
            print("--- Croatian Parser Test ---")
            print(parsed.json(indent=2, ensure_ascii=False))
        except ValueError as e:
            logger.error(f"Parsing error: {e}")

        error_cases = [
            RawCroatianData(word="", source="omw_v1"),
            RawCroatianData(word="stol", source="omw_v1", pos="wrongpos")
        ]
        for case in error_cases:
            try:
                print(f"\n--- Error Case: {case} ---")
                parsed = await parse_croatian_data(case)
                print(parsed.json(indent=2))
            except ValueError as e:
                logger.warning(f"Test case failed: {e}")

        json_path = Path("dict_hr_2letter.json")
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            for entry in json_data[:2]:
                try:
                    raw = RawCroatianData(**entry)
                    parsed = await parse_croatian_data(raw)
                    print(f"\n--- JSON Test: {raw.word} ---")
                    print(parsed.json(indent=2, ensure_ascii=False))
                except ValueError as e:
                    logger.warning(f"JSON test failed for {entry.get('word', 'unknown')}: {e}")

    asyncio.run(main())