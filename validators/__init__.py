# dictionary_project/validators/__init__.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from .schema_validator import validate_entry_data, log_validation_error
from .custom_validator import (
    validate_german_features, 
    validate_korean_features, 
    validate_japanese_features,
    validate_croatian_features
)
from pydantic import ValidationError
from schemas.base import BaseFeatures
from typing import List, Tuple
from multiprocessing import Pool

CUSTOM_VALIDATORS = {
    "de": validate_german_features,
    "ko": validate_korean_features,
    "ja": validate_japanese_features,
    "hr": validate_croatian_features,
}

def validate_entry(entry_data: dict) -> Tuple[bool, str]:
    """
    Perform full validation (schema + custom) for a single entry.
    Returns (True, "") on success, (False, error_message) on failure.
    """
    try:
        validated_obj = validate_entry_data(entry_data)
        if not validated_obj.senses:
            error_msg = "Validation Error: 'senses' field is empty."
            import asyncio
            asyncio.run(log_validation_error(entry_data, {"custom_error": error_msg}))
            return False, error_msg
        first_sense = validated_obj.senses[0]
        for lang, features in first_sense.translations.items():
            if lang in CUSTOM_VALIDATORS:
                if not isinstance(features, BaseFeatures):
                    continue
                validator_fn = CUSTOM_VALIDATORS[lang]
                is_valid, error_msg = validator_fn(features)
                if not is_valid:
                    detailed_msg = f"[{lang}] {error_msg}"
                    import asyncio
                    asyncio.run(log_validation_error(entry_data, {"custom_error": detailed_msg}))
                    return False, detailed_msg
    except ValidationError as e:
        return False, f"Schema Validation Error: {str(e)}"
    return True, ""

def validate_batch(entries: List[dict]) -> List[Tuple[bool, str]]:
    """Validate multiple entries in parallel."""
    with Pool() as pool:
        return pool.map(validate_entry, entries)