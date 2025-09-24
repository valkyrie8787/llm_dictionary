# dictionary_project/utils/data_loader.py
# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

from pathlib import Path
from typing import Dict, List, Any
from schemas.base import Sense
from pydantic import BaseModel
import logging

# 각 파서의 RawData 모델들을 모두 임포트합니다.
from lang_plugins.de_parser import RawGermanData
from lang_plugins.ko_parser import RawKoreanData
from lang_plugins.en_parser import RawEnglishData
from lang_plugins.hr_parser import RawCroatianData
from lang_plugins.es_parser import RawSpanishData
from lang_plugins.fr_parser import RawFrenchData
from lang_plugins.ja_parser import RawJapaneseData
from lang_plugins.zh_parser import RawChineseData

logger = logging.getLogger(__name__)

# 언어 코드와 RawData 모델을 매핑합니다.
RAW_DATA_MODELS = {
    "de": RawGermanData, "ko": RawKoreanData, "en": RawEnglishData,
    "hr": RawCroatianData, "es": RawSpanishData, "fr": RawFrenchData,
    "ja": RawJapaneseData, "zh": RawChineseData,
}

# 각 언어 데이터 파일의 실제 위치를 중앙에서 관리합니다.
LANGUAGE_DATA_PATHS = {
    # OMW 1.4 패키지에 포함된 언어들
    "hr": Path("offline_resources/omw-1.4/hrv/wn-data-hrv.tab"),
    "ja": Path("offline_resources/omw-1.4/jpn/wn-data-jpn.tab"),
    "fr": Path("offline_resources/omw-1.4/fra/wn-data-fra.tab"),
    
    # 별도로 다운로드한 언어들
    "en": Path("offline_resources/wordnet-3.0/dict/data.noun"),
    # "ko": Path("offline_resources/korean_wordnet/kor_wordnet.tab"), # 예시 경로
    # "de": Path("offline_resources/germanet/deu_germanet.tab"),      # 예시 경로
    # "es": Path("offline_resources/omw-1.4/spa/wn-data-spa.tab"),    # 예시 경로
    # "zh": Path("offline_resources/omw-1.4/cmn/wn-data-cmn.tab"),    # 예시 경로
}

def _parse_tab_file_for_sense(file_path: Path, sense_id: str) -> Dict[str, Any]:
    """
    하나의 .tab 파일에서 특정 sense_id에 대한 정보를 추출합니다.
    이 함수는 실제 OMW 데이터 포맷에 맞춰 정교하게 구현되어야 합니다.
    """
    extracted_info = {"lemmas": [], "definitions": [], "examples": []}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # 매우 단순화된 파싱 로직 예시
                if line.startswith(sense_id):
                    parts = line.strip().split('\t')
                    if len(parts) < 3:
                        continue
                    
                    data_type = parts[1]
                    value = parts[2]

                    if data_type.endswith(":lemma"):
                        extracted_info["lemmas"].append(value)
                    elif data_type.endswith(":def"):
                        extracted_info["definitions"].append(value)
                    elif data_type.endswith(":exe"):
                        extracted_info["examples"].append(value)

    except FileNotFoundError:
        logger.warning(f"Data file not found: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {e}")
        return {}
        
    return extracted_info

async def load_raw_data_for_sense(sense: Sense, languages: List[str]) -> Dict[str, BaseModel]:
    """
    주어진 Sense ID에 대해, 요청된 언어들의 원본 데이터를 파일에서 로드합니다.
    """
    raw_data_objects = {}
    sense_id_key = sense.sense_id.replace("wn:", "")

    for lang_code in languages:
        data_file_path = LANGUAGE_DATA_PATHS.get(lang_code)

        if not data_file_path or not data_file_path.exists():
            logger.warning(f"Data file path for language '{lang_code}' is not defined or file not found.")
            continue

        parsed_info = _parse_tab_file_for_sense(data_file_path, sense_id_key)
        
        if not parsed_info or not parsed_info.get("lemmas"):
            continue
            
        # 추출된 정보를 RawData 모델에 맞게 조립합니다.
        # TODO: 성별(gender), 격변화(declensions) 등은 다른 파일이나 규칙에서 가져와야 할 수 있습니다.
        assembled_data = {
            "word": parsed_info["lemmas"][0], # 첫 번째 단어를 대표로 사용
            "source": f"omw_v1_{lang_code}", # 소스 정보도 경로 설정에서 관리 가능
            "pos": None, # .tab 파일에는 품사 정보가 없어 별도 처리가 필요
            "examples": parsed_info["examples"],
            "definition_target": parsed_info["definitions"][0] if parsed_info.get("definitions") else None,
        }
        
        if assembled_data:
            try:
                RawDataModel = RAW_DATA_MODELS[lang_code]
                raw_data_objects[lang_code] = RawDataModel(**assembled_data)
            except Exception as e:
                logger.error(f"Failed to create RawData object for lang '{lang_code}': {e}")

    return raw_data_objects