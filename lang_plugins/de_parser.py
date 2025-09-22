# dictionary_project/lang_plugins/de_parser.py (v2.2, Refactored)

# ✅ 수정: 새로 만든 표준 모듈 임포트
from schemas.base import GermanFeatures, ValueField, Provenance, Inflection, PosType
from utils.confidence import assign_confidence
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 입력 데이터 모델 정의
class RawGermanData(BaseModel):
    word: str
    source: str = "omw_v1" # ✅ 수정: 소스 이름을 confidence.py의 규칙과 일치시킴
    pos: Optional[str] = None
    # ... (이하 RawGermanData의 다른 필드는 이전과 동일)
    gender: Optional[str] = None
    plural: Optional[str] = None
    declensions: Dict[str, str] = {}
    examples: List[str] = []
    prompt_id: Optional[str] = None
    generated_by: str = "gpt-oss-120b-v1.0"

# ✅ 추가: 원본 POS 태그를 표준 PosType으로 변환하는 함수
def _map_pos_tag(raw_pos: Optional[str]) -> Optional[PosType]:
    if not raw_pos:
        return None
    
    mapping = {
        "Substantiv": PosType.NOUN,
        "Verb": PosType.VERB,
        # ... 다른 독일어 품사 태그 매핑 추가 ...
    }
    
    return mapping.get(raw_pos, PosType.OTHER) # 매핑에 없으면 OTHER로 처리


def parse_german_data(raw_data: RawGermanData) -> GermanFeatures:
    provenance = Provenance(...) # 이전과 동일

    # ✅ 수정: 모든 confidence 값을 assign_confidence 함수로 할당
    word_target_vf = ValueField(
        value=raw_data.word,
        provenance=provenance,
        confidence=assign_confidence(raw_data.source, "word")
    )

    gender_vf = ValueField(
        value=raw_data.gender,
        provenance=provenance,
        confidence=assign_confidence(raw_data.source, "gender")
    ) if raw_data.gender else None

    # ✅ 수정: 표준화된 PosType 사용
    standard_pos = _map_pos_tag(raw_data.pos)
    part_of_speech_vf = ValueField(
        value=standard_pos.value if standard_pos else None,
        provenance=provenance,
        confidence=assign_confidence(raw_data.source, "pos")
    ) if standard_pos else None
    
    # ... (plural, declensions, examples 등 다른 필드도 모두 assign_confidence 사용하도록 수정) ...
    plural_vf = ValueField(...)
    declension_table = [...]
    examples = [...]
    
    return GermanFeatures(
        word_target=word_target_vf,
        gender=gender_vf,
        plural=plural_vf,
        part_of_speech=part_of_speech_vf,
        declension_table=declension_table,
        examples=examples
    )