# dictionary_project/utils/confidence.py
DEFAULT_CONFIDENCE = {
    "word": 0.98, "pos": 0.95, "gender": 0.99, "plural": 0.97, "aspect": 0.98,
    "definition": 0.90, "examples": 0.90, "default": 0.95
}
SOURCE_CONFIDENCE = {
    "wordnet_3.0": 1.0, "omw_v1": 0.95,
    "gpt-oss:20b": 0.85, "llm:gpt-oss-120b": 0.80
}
def assign_confidence(source: str, field_key: str) -> float:
    base_confidence = SOURCE_CONFIDENCE.get(source, 0.90)
    field_confidence_weight = DEFAULT_CONFIDENCE.get(field_key, DEFAULT_CONFIDENCE["default"])
    return round(base_confidence * field_confidence_weight, 4)