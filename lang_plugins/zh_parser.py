# dictionary_project/lang_plugins/zh_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import ChineseFeatures, Inflection, Provenance
from utils.helpers import create_value_field, map_pos_tag
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

class RawChineseData(BaseModel):
    word: str
    source: str
    pos: Optional[str] = None
    simplified: Optional[str] = None
    traditional: Optional[str] = None
    pinyin: Optional[str] = None
    tones: Optional[str] = None
    measure_words: Dict[str, str] = {}
    examples: List[str] = []
    definition_target: Optional[str] = None
    example_target: Optional[str] = None
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"
    source_licenses: Optional[Dict[str, str]] = None

async def parse_chinese_data(raw_data: RawChineseData) -> ChineseFeatures:
    if not raw_data.word:
        raise ValueError("Field 'word' cannot be empty.")
    provenance = Provenance(source=raw_data.source, prompt_id=raw_data.prompt_id, generated_by=raw_data.generated_by)
    standard_pos = map_pos_tag(raw_data.pos, "zh")
    all_examples = raw_data.examples[:]
    if raw_data.example_target:
        all_examples.append(raw_data.example_target)

    return ChineseFeatures(
        word_target=await create_value_field(raw_data.word, "word", provenance, lang="zh"),
        part_of_speech=await create_value_field(standard_pos.value if standard_pos else None, "pos", provenance, lang="zh"),
        definition=await create_value_field(raw_data.definition_target, "definition", provenance, lang="zh"),
        simplified=await create_value_field(raw_data.simplified, "simplified", provenance, lang="zh"),
        traditional=await create_value_field(raw_data.traditional, "traditional", provenance, lang="zh"),
        pinyin=await create_value_field(raw_data.pinyin, "pinyin", provenance, lang="zh"),
        tones=await create_value_field(raw_data.tones, "tones", provenance, lang="zh"),
        measure_words=[
            Inflection(form=await create_value_field(form, m_word, provenance, lang="zh"), type=m_word)
            async for m_word, form in raw_data.measure_words.items()
        ],
        examples=[
            await create_value_field(ex, "examples", provenance, lang="zh")
            async for ex in all_examples
        ]
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    async def main():
        sample_data = RawChineseData(
            word="桌子",
            source="omw_v1",
            pos="名词",
            pinyin="zhuōzi",
            definition_target="有腿的、上面放东西的家具。",
            source_licenses={"omw": "Princeton License"}
        )
        try:
            parsed = await parse_chinese_data(sample_data)
            print("--- Chinese Parser Test ---")
            print(parsed.json(indent=2, ensure_ascii=False))
        except ValueError as e:
            logger.error(f"Parsing error: {e}")

        error_cases = [
            RawChineseData(word="", source="omw_v1"),
            RawChineseData(word="桌子", source="omw_v1", pos="wrongpos")
        ]
        for case in error_cases:
            try:
                print(f"\n--- Error Case: {case} ---")
                parsed = await parse_chinese_data(case)
                print(parsed.json(indent=2))
            except ValueError as e:
                logger.warning(f"Test case failed: {e}")

        json_path = Path("dict_zh_2letter.json")
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            for entry in json_data[:2]:
                try:
                    raw = RawChineseData(**entry)
                    parsed = await parse_chinese_data(raw)
                    print(f"\n--- JSON Test: {raw.word} ---")
                    print(parsed.json(indent=2, ensure_ascii=False))
                except ValueError as e:
                    logger.warning(f"JSON test failed for {entry.get('word', 'unknown')}: {e}")

    asyncio.run(main())