# dictionary_project/lang_plugins/ko_parser.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import KoreanFeatures, Inflection, Provenance
from utils.helpers import create_value_field, map_pos_tag
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

class RawKoreanData(BaseModel):
    word: str
    source: str
    pos: Optional[str] = None
    hanja: Optional[str] = None
    romanization: Optional[str] = None
    conjugations: Dict[str, str] = {}
    examples: List[str] = []
    definition_target: Optional[str] = None
    example_target: Optional[str] = None
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"
    source_licenses: Optional[Dict[str, str]] = None  # e.g., {"omw": "Princeton License"}

async def parse_korean_data(raw_data: RawKoreanData) -> KoreanFeatures:
    if not raw_data.word:
        raise ValueError("Field 'word' cannot be empty.")
    provenance = Provenance(source=raw_data.source, prompt_id=raw_data.prompt_id, generated_by=raw_data.generated_by)
    standard_pos = map_pos_tag(raw_data.pos, "ko")
    all_examples = raw_data.examples[:]
    if raw_data.example_target:
        all_examples.append(raw_data.example_target)

    return KoreanFeatures(
        word_target=await create_value_field(raw_data.word, "word", provenance, lang="ko"),
        part_of_speech=await create_value_field(standard_pos.value if standard_pos else None, "pos", provenance, lang="ko"),
        hanja=await create_value_field(raw_data.hanja, "hanja", provenance, lang="ko"),
        romanization=await create_value_field(raw_data.romanization, "romanization", provenance, lang="ko"),
        conjugation_samples=[
            Inflection(form=await create_value_field(form, c_type, provenance, lang="ko"), type=c_type)
            async for c_type, form in raw_data.conjugations.items()
        ],
        examples=[
            await create_value_field(ex, "examples", provenance, lang="ko")
            async for ex in all_examples
        ],
        definition=await create_value_field(raw_data.definition_target, "definition", provenance, lang="ko")
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    async def main():
        # 샘플 데이터 테스트
        sample_data = RawKoreanData(
            word="책상",
            source="omw_v1",
            pos="명사",
            hanja="卓床",
            examples=["책상에 책이 있다."],
            definition_target="책상은 책이나 물건을 올려놓는 가구이다.",
            source_licenses={"omw": "Princeton License"}
        )
        try:
            parsed = await parse_korean_data(sample_data)
            print("--- Korean Parser Test ---")
            print(parsed.json(indent=2, ensure_ascii=False))
        except ValueError as e:
            logger.error(f"Parsing error: {e}")

        # 에러 케이스 테스트
        error_cases = [
            RawKoreanData(word="", source="omw_v1"),  # 빈 word
            RawKoreanData(word="책상", source="omw_v1", pos="잘못된품사")  # 잘못된 pos
        ]
        for case in error_cases:
            try:
                print(f"\n--- Error Case: {case} ---")
                parsed = await parse_korean_data(case)
                print(parsed.json(indent=2))
            except ValueError as e:
                logger.warning(f"Test case failed: {e}")

        # JSON 데이터 테스트
        json_path = Path("dict_ko_2letter.json")
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            for entry in json_data[:2]:
                try:
                    raw = RawKoreanData(**entry)
                    parsed = await parse_korean_data(raw)
                    print(f"\n--- JSON Test: {raw.word} ---")
                    print(parsed.json(indent=2, ensure_ascii=False))
                except ValueError as e:
                    logger.warning(f"JSON test failed for {entry.get('word', 'unknown')}: {e}")

    asyncio.run(main())