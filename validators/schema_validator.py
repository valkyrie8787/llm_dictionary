# dictionary_project/validators/schema_validator.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from pydantic import ValidationError
from schemas.base import DictionaryRoot
import json
from datetime import datetime
import aiofiles

async def log_validation_error(data: dict, error_message: str | list):
    """Log validation failures in jsonl format asynchronously."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "invalid_data": data,
        "error": error_message
    }
    async with aiofiles.open("validation_log.jsonl", "a", encoding="utf-8") as f:
        await f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def validate_entry_data(data: dict) -> DictionaryRoot:
    """
    Validate data structure using Pydantic DictionaryRoot model.
    Returns validated object or raises ValidationError with logging.
    """
    try:
        entry = DictionaryRoot.parse_obj(data)
        return entry
    except ValidationError as e:
        import asyncio
        asyncio.run(log_validation_error(data, e.errors()))
        raise# dictionary_project/validators/schema_validator.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from pydantic import ValidationError
from schemas.base import DictionaryRoot
import json
from datetime import datetime
import aiofiles

async def log_validation_error(data: dict, error_message: str | list):
    """Log validation failures in jsonl format asynchronously."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "invalid_data": data,
        "error": error_message
    }
    async with aiofiles.open("validation_log.jsonl", "a", encoding="utf-8") as f:
        await f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def validate_entry_data(data: dict) -> DictionaryRoot:
    """
    Validate data structure using Pydantic DictionaryRoot model.
    Returns validated object or raises ValidationError with logging.
    """
    try:
        entry = DictionaryRoot.parse_obj(data)
        return entry
    except ValidationError as e:
        import asyncio
        asyncio.run(log_validation_error(data, e.errors()))
        raise