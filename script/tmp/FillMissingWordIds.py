#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meaning.csv에서 word_id 1~600 중 없는 항목을 채우는 스크립트
누락된 word_id에 대해 DefId=0, Meaning="TempWord_{word_id}", part_of_speech="null" 추가
사용법: python script/tmp/FillMissingword_ids.py [input_file] [output_file]
"""

import csv
import sys
import os

def fill_missing_word_ids(input_file, output_file=None):
    """
    Meaning.csv에서 word_id 1~600 중 없는 항목을 채우기
    
    Args:
        input_file: 입력 CSV 파일 경로
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일 덮어쓰기)
    """
    # 파일 존재 확인
    if not os.path.exists(input_file):
        print(f"오류: CSV 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if output_file is None:
        output_file = input_file
    
    # 기존 데이터 읽기
    existing_word_ids = set()
    rows = []
    fieldnames = None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None:
            print("오류: CSV 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        for row in reader:
            word_id = row.get('word_id', '').strip()
            if word_id:
                try:
                    word_id_int = int(word_id)
                    existing_word_ids.add(word_id_int)
                except ValueError:
                    pass
            rows.append(row)
    
    # 1~600 중 없는 word_id 찾기
    all_word_ids = set(range(1, 601))
    missing_word_ids = sorted(all_word_ids - existing_word_ids)
    
    print(f"기존 word_id 개수: {len(existing_word_ids)}")
    print(f"누락된 word_id 개수: {len(missing_word_ids)}")
    
    if not missing_word_ids:
        print("모든 word_id가 이미 존재합니다. 추가할 항목이 없습니다.")
        return
    
    # 누락된 word_id에 대해 새 행 추가
    new_rows = []
    for word_id in missing_word_ids:
        # sense_no 계산: word_id * 10 + DefId (DefId=0)
        mean_id = word_id * 10 + 0
        
        new_row = {
            'word_id': str(word_id),
            'DefId': '0',
            'sense_no': str(mean_id),
            'Meaning': f'TempWord_{word_id}',
            'part_of_speech': 'null'
        }
        new_rows.append(new_row)
        rows.append(new_row)
    
    # word_id로 정렬 (숫자로 변환하여 정렬)
    def sort_key(row):
        try:
            return int(row.get('word_id', '0'))
        except ValueError:
            return 0
    
    rows.sort(key=sort_key)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  추가된 행: {len(new_rows)}개")
    if new_rows:
        print(f"  예시 (처음 5개):")
        for row in new_rows[:5]:
            print(f"    word_id={row['word_id']}, sense_no={row['sense_no']}, Meaning={row['Meaning']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/tmp/FillMissingword_ids.py <input_file> [output_file]")
        print("예시: python script/tmp/FillMissingword_ids.py data/Meaning.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    fill_missing_word_ids(input_file, output_file)

