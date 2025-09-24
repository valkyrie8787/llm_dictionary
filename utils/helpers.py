# dictionary_project/utils/helpers.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import ValueField, Provenance, PosType
from utils.confidence import assign_confidence
from typing import Optional, Dict
import logging
import json
import aiofiles
from datetime import datetime

logger = logging.getLogger(__name__)

async def create_value_field(value: Optional[str], key: str, provenance: Provenance, lang: str = "unknown") -> Optional[ValueField]:
    if value is not None and value != "":
        confidence = assign_confidence(provenance.source, key)
        return ValueField(value=value, provenance=provenance, confidence=confidence)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "lang": lang,
        "key": key,
        "source": provenance.source,
        "error": "Missing or empty field",
        "severity": "warning"
    }
    async with aiofiles.open("parser_log.jsonl", "a", encoding="utf-8") as f:
        await f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    return None

def map_pos_tag(raw_pos: Optional[str], lang: str) -> Optional[PosType]:
    if not raw_pos:
        return None
    mappings = {
        "de": {"Substantiv": PosType.NOUN, "Verb": PosType.VERB, "Adjektiv": PosType.ADJ},
        "ko": {"명사": PosType.NOUN, "동사": PosType.VERB, "형용사": PosType.ADJ},
        "ja": {"名詞": PosType.NOUN, "動詞": PosType.VERB, "形容詞": PosType.ADJ},
        "en": {"noun": PosType.NOUN, "verb": PosType.VERB, "adjective": PosType.ADJ},
        "hr": {"imenica": PosType.NOUN, "glagol": PosType.VERB, "pridjev": PosType.ADJ},
        "es": {"nombre": PosType.NOUN, "verbo": PosType.VERB, "adjetivo": PosType.ADJ},
        "fr": {"nom": PosType.NOUN, "verbe": PosType.VERB, "adjectif": PosType.ADJ},
        "zh": {"名词": PosType.NOUN, "动词": PosType.VERB, "形容词": PosType.ADJ},
    }
    lang_mapping = mappings.get(lang, {})
    return lang_mapping.get(raw_pos)