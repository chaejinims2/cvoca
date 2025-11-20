#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
day_no 파일의 단어들을 words.csv에 대체하는 스크립트

사용법:
    python script/update_words_from_day_file.py <day_file> <words_csv>

예시:
    python script/update_words_from_day_file.py data/ielts_voca_20_30/user/4.csv data/ielts_voca_20_30/user/words.csv
"""

import csv
import sys
import os


def update_words_from_day_file(day_file, words_csv):
    """
    day_no 파일의 단어들을 words.csv에 대체
    
    지원하는 형식:
    1. CSV 형식: day_no,word 또는 word_id,word (헤더 포함)
    2. 텍스트 형식: 한 줄에 하나씩 단어만
    
    Args:
        day_file: day_no 파일 경로 (예: 4.csv 또는 14.csv)
        words_csv: words.csv 파일 경로
    """
    # 파일 존재 확인
    if not os.path.exists(day_file):
        print(f"오류: 파일 '{day_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if not os.path.exists(words_csv):
        print(f"오류: 파일 '{words_csv}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # day_no 추출 (파일명에서 확장자 제거)
    day_filename = os.path.basename(day_file)
    day_no_str = os.path.splitext(day_filename)[0]
    
    try:
        day_no = int(day_no_str)
    except ValueError:
        print(f"오류: 파일명 '{day_filename}'에서 day_no를 추출할 수 없습니다.")
        print("      파일명은 숫자여야 합니다 (예: 4.csv)")
        sys.exit(1)
    
    print(f"day_no: {day_no}")
    
    # day_file에서 단어 읽기 (CSV 형식 또는 단순 텍스트 형식 지원)
    words = []
    word_id_to_word = {}  # word_id를 키로 하는 딕셔너리
    
    with open(day_file, 'r', encoding='utf-8') as f:
        # CSV 형식인지 확인 (첫 줄이 헤더인지 확인)
        first_line = f.readline().strip()
        f.seek(0)  # 파일 포인터 리셋
        
        reader = csv.reader(f)
        first_row = next(reader, None)
        
        if first_row and len(first_row) >= 2:
            # CSV 형식인지 확인 (헤더가 있는지, 첫 번째 컬럼이 숫자로 변환 가능한지)
            is_csv_format = False
            if first_row[0].lower() in ['word_id', 'day_no']:
                # 헤더가 있는 CSV 형식 (word_id 우선)
                is_csv_format = True
            else:
                # 헤더가 없지만 첫 번째 값이 숫자면 CSV 형식으로 간주
                try:
                    int(first_row[0])
                    is_csv_format = True
                except ValueError:
                    pass
            
            if is_csv_format:
                # CSV 형식 (day_no,word 또는 word_id,word)
                print("CSV 형식으로 읽는 중...")
                # 첫 번째 행이 헤더인지 확인
                skip_first = first_row[0].lower() in ['day_no', 'word_id']
                
                if not skip_first:
                    # 헤더가 없으면 첫 번째 행도 데이터로 처리
                    try:
                        word_id = int(first_row[0])
                        word = first_row[1].strip() if len(first_row) > 1 else ''
                        if word:
                            word_id_to_word[word_id] = word
                    except ValueError:
                        pass
                
                for row in reader:
                    if len(row) >= 2:
                        try:
                            word_id = int(row[0])
                            word = row[1].strip()
                            if word:  # 빈 단어 제외
                                word_id_to_word[word_id] = word
                        except ValueError:
                            continue
        else:
            # 단순 텍스트 형식 (한 줄에 하나씩)
            print("텍스트 형식으로 읽는 중...")
            f.seek(0)  # 파일 포인터 리셋
            for line in f:
                word = line.strip()
                if word:  # 빈 줄 제외
                    words.append(word)
    
    # CSV 형식이면 words 리스트로 변환 (word_id 순서대로)
    if word_id_to_word:
        sorted_word_ids = sorted(word_id_to_word.keys())
        words = [word_id_to_word[wid] for wid in sorted_word_ids]
        print(f"읽은 단어 수: {len(words)}개 (word_id: {min(sorted_word_ids)} ~ {max(sorted_word_ids)})")
    else:
        if not words:
            print(f"오류: '{day_file}' 파일에 단어가 없습니다.")
            sys.exit(1)
        print(f"읽은 단어 수: {len(words)}개")
    
    # words.csv 읽기
    rows = []
    with open(words_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        if not fieldnames:
            print(f"오류: '{words_csv}' 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        # 필수 컬럼 확인
        if 'day_no' not in fieldnames:
            print(f"오류: '{words_csv}' 파일에 'day_no' 컬럼이 없습니다.")
            sys.exit(1)
        
        if 'word' not in fieldnames:
            print(f"오류: '{words_csv}' 파일에 'word' 컬럼이 없습니다.")
            sys.exit(1)
        
        # 모든 행 읽기
        for row in reader:
            rows.append(row)
    
    print(f"words.csv 총 행 수: {len(rows)}개 (헤더 제외)")
    
    # day_no에 해당하는 행 찾기 및 업데이트
    updated_count = 0
    word_index = 0
    
    # word_id 기반 매핑이 있는 경우 (CSV 형식에서 읽었을 때)
    if word_id_to_word:
        # word_id 컬럼 확인
        if 'word_id' not in fieldnames:
            print(f"경고: '{words_csv}' 파일에 'word_id' 컬럼이 없어 word_id 기반 매핑을 사용할 수 없습니다.")
            print("      순서 기반 매핑으로 전환합니다.")
            word_id_to_word = {}  # 비활성화
    
    for row in rows:
        try:
            row_day_no = int(row['day_no'])
            if row_day_no == day_no:
                # word_id 기반 매핑 사용
                if word_id_to_word and 'word_id' in row:
                    try:
                        row_word_id = int(row['word_id'])
                        if row_word_id in word_id_to_word:
                            row['word'] = word_id_to_word[row_word_id]
                            updated_count += 1
                        else:
                            print(f"경고: word_id={row_word_id}에 해당하는 단어가 없습니다.")
                    except ValueError:
                        continue
                # 순서 기반 매핑 사용
                else:
                    if word_index < len(words):
                        row['word'] = words[word_index]
                        updated_count += 1
                        word_index += 1
                    else:
                        print(f"경고: day_no={day_no}인 행이 {len(words)}개보다 많습니다.")
                        print(f"      {updated_count}개 행만 업데이트되었습니다.")
                        break
        except ValueError:
            print(f"경고: day_no 값이 숫자가 아닌 행을 건너뜁니다: {row.get('day_no', 'N/A')}")
            continue
    
    if updated_count == 0:
        print(f"경고: day_no={day_no}인 행을 찾을 수 없습니다.")
        sys.exit(1)
    
    if word_index < len(words):
        print(f"경고: {len(words) - word_index}개의 단어가 사용되지 않았습니다.")
    
    # 업데이트된 내용을 파일에 쓰기
    with open(words_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n=== 업데이트 완료 ===")
    print(f"업데이트된 행 수: {updated_count}개")
    print(f"파일: {words_csv}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("사용법: python script/update_words_from_day_file.py <day_file> <words_csv>")
        print("\n예시:")
        print("  python script/update_words_from_day_file.py data/ielts_voca_20_30/user/4.csv data/ielts_voca_20_30/user/words.csv")
        sys.exit(1)
    
    day_file = sys.argv[1]
    words_csv = sys.argv[2]
    
    update_words_from_day_file(day_file, words_csv)

