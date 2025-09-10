import json
import re

def extract_ko_keyword(entry):
    """
    한국어 예문에서 목적격 조사를 이용하여 명사를 추출합니다.
    예: '동물원을 방문했다' -> '동물원'
    """
    example = entry.get('example_target', '')
    # '을/를', '으로/로', '은/는', '이/가'로 끝나는 단어를 찾습니다.
    match = re.search(r'(\S+)(을|를|으로|로|은|는|이|가)\s', example)
    if match:
        return match.group(1)
    return None

def extract_de_keyword(entry):
    """
    독일어 정의에서 첫 번째 명사(대문자로 시작)를 추출합니다.
    예: 'Ein Tierpark, in dem...' -> 'Tierpark'
    """
    definition = entry.get('definition_target', '')
    # 문장에서 대문자로 시작하는 단어들을 찾습니다.
    words = re.findall(r'\b[A-Z][a-z]+\b', definition)
    if len(words) > 1:
        # 'Ein', 'Eine' 같은 관사를 제외하기 위해 두 번째 단어를 주로 선택
        return words[1] if words[0] in ['Ein', 'Eine', 'Der', 'Die', 'Das'] and len(words) > 1 else words[0]
    elif words:
        return words[0]
    return None

def process_file(input_path, output_path, lang_code, extractor_func):
    """
    JSON 파일을 읽고, 키워드를 추출하여 새 파일에 저장합니다.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: '{input_path}' 파일을 찾을 수 없습니다.")
        return

    entries = data.get('entries') or data.get('words', [])
    processed_count = 0
    
    for entry in entries:
        keyword = extractor_func(entry)
        if keyword:
            entry[f'word_{lang_code}'] = keyword
            processed_count += 1
            
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"'{output_path}' 파일 생성 완료. 총 {processed_count}개의 대표 단어 키를 추가했습니다.")

if __name__ == '__main__':
    print("대표 단어 키 추가 작업을 시작합니다...")
    process_file('dict_ko.json', 'dict_ko_extended.json', 'ko', extract_ko_keyword)
    process_file('dict_de.json', 'dict_de_extended.json', 'de', extract_de_keyword)
    print("작업 완료.")