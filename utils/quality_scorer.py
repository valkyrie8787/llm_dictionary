# dictionary_project/utils/quality_scorer.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from schemas.base import DictionaryRoot
from typing import Dict
from sentence_transformers import SentenceTransformer, util
import logging

logger = logging.getLogger(__name__)

# ✅ 1. 임베딩 모델 로드 (프로그램 시작 시 한 번만 로드)
# 전 세계적으로 널리 사용되는 경량 모델을 사용합니다.
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    logger.error(f"Failed to load sentence-transformer model. Please install it: pip install sentence-transformers. Error: {e}")
    embedding_model = None

async def _calculate_back_translation_score(original_text: str, translated_text: str) -> Dict[str, float]:
    """
    역번역을 수행하고 원본과의 임베딩 유사도 점수를 계산합니다.
    """
    if not embedding_model:
        return {"embedding_similarity": 0.0, "bleu_score": 0.0}
        
    # TODO: 이 부분에 실제 역번역을 수행하는 API나 모델 호출 로직이 필요합니다.
    # 예: back_translated_text = await translate_api(translated_text, target_lang="en")
    # 지금은 테스트를 위해 번역된 텍스트를 그대로 사용합니다.
    back_translated_text = translated_text 
    
    # ✅ 2. 실제 임베딩 및 코사인 유사도 계산
    try:
        original_embedding = embedding_model.encode(original_text, convert_to_tensor=True)
        back_translated_embedding = embedding_model.encode(back_translated_text, convert_to_tensor=True)
        
        cosine_scores = util.cos_sim(original_embedding, back_translated_embedding)
        embedding_sim = round(cosine_scores.item(), 4)
    except Exception as e:
        logger.error(f"Error calculating embedding similarity: {e}")
        embedding_sim = 0.0
    
    # TODO: BLEU 점수 계산 로직 추가
    bleu_score = 0.0 # 임시값

    return {"embedding_similarity": embedding_sim, "bleu_score": bleu_score}

async def _perform_cross_check(word: str, lang: str) -> bool:
    """
    Wiktionary 등 외부 사전에 해당 단어가 존재하는지 확인합니다.
    """
    # TODO: 이 부분에 offline_resources에 있는 Wiktionary 등
    # 대조용 사전 데이터를 조회하는 실제 로직이 필요합니다.
    # 예: return word in wiktionary_set_for_lang
    
    return True # 임시로 항상 True 반환

async def calculate_quality_scores(entry: DictionaryRoot) -> Dict[str, Dict[str, float | bool]]:
    quality_scores = {}
    
    if not entry.senses:
        return {}
        
    first_sense = entry.senses[0]
    english_example = first_sense.examples_en[0] if first_sense.examples_en else entry.word_en

    for lang, features in first_sense.translations.items():
        if not features.examples:
            continue
            
        translated_example = features.examples[0].value

        # 1. 역번역 점수 계산
        back_trans_scores = await _calculate_back_translation_score(english_example, translated_example)
        
        # 2. 교차 검증 수행
        cross_check_found = await _perform_cross_check(features.word_target.value, lang)

        # 3. 최종 점수 계산
        final_score = round(0.8 * back_trans_scores["embedding_similarity"] + 0.2 * back_trans_scores["bleu_score"], 4)
        
        quality_scores[lang] = {
            "embedding_similarity": back_trans_scores["embedding_similarity"],
            "bleu_score": back_trans_scores["bleu_score"],
            "final_score": final_score,
            "cross_check_found": cross_check_found
        }
        
    return quality_scores