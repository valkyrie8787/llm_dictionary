# dictionary_project/utils/confidence.py

def assign_confidence(source: str, field_key: str) -> float:
    """
    데이터의 출처와 필드 종류에 따라 표준화된 신뢰도 점수를 반환합니다.
    이곳에서 프로젝트의 모든 신뢰도 정책을 관리합니다.
    """
    
    # 규칙 기반: 출처별 신뢰도 규칙 정의
    rules = {
        "omw_v1": {
            "default": 0.95,
            "word": 0.98,
            "gender": 0.99, # 규칙으로 명확히 추출 가능하므로 신뢰도 높음
            "plural": 0.97,
            "examples": 0.90
        },
        "llm_gpt-oss-120b": {
            "default": 0.85,
            "examples": 0.80 # LLM이 생성한 예문은 신뢰도를 약간 낮게 설정
        }
        # ... 다른 소스에 대한 규칙 추가 ...
    }
    
    # 소스와 필드 키에 맞는 신뢰도 점수를 찾아 반환
    source_rules = rules.get(source, {})
    return source_rules.get(field_key, source_rules.get("default", 0.75)) # 기본값이 없으면 0.75