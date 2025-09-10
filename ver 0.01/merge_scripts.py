import json
from collections import OrderedDict

# --- 1. 설정: 처리할 파일과 결과 파일 경로 지정 ---
FILES_TO_PROCESS = {
    'ja': 'dict_ja.json',  
    'ko': 'dict_ko.json',  
    'de': 'dict_de.json'   
}
OUTPUT_FILE_PATH = 'multilingual_dict.json'

def get_entries_from_data(data):
    """'entries' 또는 'words' 키를 확인하여 단어 리스트를 안전하게 반환합니다."""
    return data.get('entries') or data.get('words', [])

def main():
    merged_data = OrderedDict()
    lang_names = {'ja': '일본어', 'ko': '한국어', 'de': '독일어'}

    # --- 2. 각 JSON 파일 불러오기 및 병합 ---
    for lang_code, file_path in FILES_TO_PROCESS.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError as e:
            print(f"오류: {e.filename} 파일을 찾을 수 없습니다. 1단계 스크립트를 먼저 실행했는지 확인하세요.")
            return

        entries = get_entries_from_data(data)
        processed_count = 0
        print(f"'{file_path}' 처리 중...")

        for entry in entries:
            word = entry.get('word')
            if not word:
                continue

            # 새로운 단어인 경우 기본 구조 생성
            if word not in merged_data:
                merged_data[word] = {
                    'word': word,
                    'pos': entry.get('pos'),
                    'definition_en': entry.get('definition_en'),
                    'example_en': entry.get('example_en'),
                    'prefix': entry.get('prefix'),
                    'length': entry.get('length'),
                    'translations': {}
                }
            
            # 번역 정보 추가
            translation_info = {
                'definition': entry.get('definition_target'),
                'example': entry.get('example_target')
            }
            
            # [수정된 부분] 모든 'word_{lang_code}' 키를 동적으로 찾아 추가
            word_key = f'word_{lang_code}'
            if word_key in entry:
                translation_info[word_key] = entry.get(word_key)

            merged_data[word]['translations'][lang_code] = translation_info
            processed_count += 1
            
        print(f"{lang_names[lang_code]} 사전 처리 완료. {processed_count}개 항목 병합.")

    # --- 3. 최종 결과물 생성 및 저장 ---
    final_data_list = list(merged_data.values())
    final_output = {
        "metadata": {
            "title": "Multilingual Dictionary (EN-JA-KO-DE)",
            "source_language": "en",
            "target_languages": list(FILES_TO_PROCESS.keys()),
            "total_entries": len(final_data_list)
        },
        "entries": final_data_list
    }

    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print(f"\n병합 완료! '{OUTPUT_FILE_PATH}' 파일이 성공적으로 생성되었습니다.")

if __name__ == '__main__':
    main()