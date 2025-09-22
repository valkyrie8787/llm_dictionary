# dictionary_project/validators/custom_validator.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import GermanFeatures, KoreanFeatures, JapaneseFeatures, CroatianFeatures, PosType
from typing import Tuple
# 가정: BLEU 점수 계산용 라이브러리
from bleurt import score as bleurt_score  # pip install bleurt

def validate_german_features(features: GermanFeatures) -> Tuple[bool, str]:
    """Validate German-specific logical rules."""
    if features.part_of_speech and features.part_of_speech.value == PosType.NOUN:
        if features.gender is None or features.gender.value is None:
            return False, f"German noun '{features.word_target.value}' is missing 'gender'."
        if features.plural is None or features.plural.value is None:
            return False, f"German noun '{features.word_target.value}' is missing 'plural'."
    if not features.examples:
        return False, f"German entry '{features.word_target.value}' is missing 'examples'."
    for ex in features.examples:
        if ex.confidence < 0.85:
            return False, f"Example '{ex.value}' for '{features.word_target.value}' has low confidence {ex.confidence}."
    return True, ""

def validate_korean_features(features: KoreanFeatures) -> Tuple[bool, str]:
    """Validate Korean-specific logical rules."""
    if features.part_of_speech and features.part_of_speech.value == PosType.VERB:
        if not features.conjugation_samples:
            return False, f"Korean verb '{features.word_target.value}' is missing 'conjugation_samples'."
    if features.hanja and not features.romanization:
        return False, f"Korean entry '{features.word_target.value}' with hanja must have romanization."
    if not features.examples:
        return False, f"Korean entry '{features.word_target.value}' is missing 'examples'."
    for ex in features.examples:
        if ex.confidence < 0.85:
            return False, f"Example '{ex.value}' for '{features.word_target.value}' has low confidence {ex.confidence}."
        # BLEU 점수 검증 (참조 예문 필요)
        # bleu = bleurt_score.compute_bleu(ex.value, reference="")  # 실제 참조 데이터 필요
        # if bleu < 0.7:
        #     return False, f"Example '{ex.value}' for '{features.word_target.value}' has low BLEU score {bleu}."
    return True, ""

def validate_japanese_features(features: JapaneseFeatures) -> Tuple[bool, str]:
    """Validate Japanese-specific logical rules."""
    if not (features.kanji or features.hiragana or features.katakana):
        return False, f"Japanese entry '{features.word_target.value}' must have at least one of 'kanji', 'hiragana', or 'katakana'."
    if not features.examples:
        return False, f"Japanese entry '{features.word_target.value}' is missing 'examples'."
    return True, ""

def validate_croatian_features(features: CroatianFeatures) -> Tuple[bool, str]:
    """Validate Croatian-specific logical rules."""
    if features.part_of_speech and features.part_of_speech.value == PosType.VERB:
        if features.aspect is None or features.aspect.value is None:
            return False, f"Croatian verb '{features.word_target.value}' is missing 'aspect'."
    if not features.examples:
        return False, f"Croatian entry '{features.word_target.value}' is missing 'examples'."
    return True, ""