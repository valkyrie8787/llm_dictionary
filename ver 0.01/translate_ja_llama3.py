import json
import requests
import time
import os
from dotenv import load_dotenv  # 1. dotenv 라이브러리에서 load_dotenv 함수 가져오기

# --- 설정 ---
load_dotenv()  # 2. .env 파일의 내용을 환경 변수로 로드

# 3. 환경 변수에서 API 토큰 불러오기 (코드에 직접 입력 X)
API_TOKEN = os.getenv("HF_API_TOKEN")

# API 토큰이 로드되었는지 확인
if not API_TOKEN:
    raise ValueError("오류: HF_API_TOKEN이 .env 파일에 설정되지 않았습니다.")

# 사용할 Llama 3 모델의 API 주소
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# 원본 및 결과물 파일 경로
INPUT_JSON_PATH = "completed_20250905_133657_comprehensive_dict_progress.json"
OUTPUT_JSON_PATH = "output_translated_ja_llama3.json"

# (이하 API 요청 함수 및 메인 로직은 이전과 동일합니다...)
# ... (이전 답변의 나머지 코드를 여기에 붙여넣으세요) ...

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def translate_with_llama3(english_word):
    """Llama 3 모델에 번역 요청을 보내고 결과를 반환하는 함수"""
    prompt = (
        f"Translate the following English word to its most common Japanese equivalent. "
        f"Respond with ONLY the single Japanese word in Hiragana, Katakana, or Kanji. Do not add any explanation or punctuation.\n\n"
        f"English: {english_word}\n"
        f"Japanese:"
    )
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 20,
            "return_full_text": False,
            "temperature": 0.1
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        translated_text = response_data[0].get('generated_text').strip()
        return translated_text
    else:
        print(f"API 오류 발생 (단어: {english_word}): {response.status_code}, 내용: {response.text}")
        if "is currently loading" in response.text:
            print("모델 로딩 중... 30초 후 재시도합니다.")
            time.sleep(30)
            return translate_with_llama3(english_word)
        return None

def main():
    try:
        with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: '{INPUT_JSON_PATH}' 파일을 찾을 수 없습니다.")
        return

    word_entries = data.get("words", [])
    total_entries = len(word_entries)
    print(f"총 {total_entries}개의 단어 번역을 시작합니다 (모델: Llama 3)...")

    for i, entry in enumerate(word_entries):
        english_word = entry.get("word")
        if "word_reverse" in entry and entry["word_reverse"]:
            print(f"[{i+1}/{total_entries}] '{english_word}' -> 이미 처리됨. 건너뜁니다.")
            continue
        if english_word:
            try:
                japanese_word = translate_with_llama3(english_word)
                if japanese_word:
                    entry["word_reverse"] = japanese_word
                    print(f"[{i+1}/{total_entries}] 성공: '{english_word}' -> '{japanese_word}'")
                else:
                    print(f"[{i+1}/{total_entries}] 실패: '{english_word}' 번역 실패.")
            except Exception as e:
                print(f"[{i+1}/{total_entries}] 오류: '{english_word}' 처리 중 예외 발생 - {e}")
        time.sleep(1)

    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✨ 작업 완료! 결과가 '{OUTPUT_JSON_PATH}'에 저장되었습니다.")

if __name__ == "__main__":
    main()