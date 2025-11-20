#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vocabulary.csv에 특정 Day에 행을 추가하는 스크립트
사용법: python script/tmp/AddRows.py data/Vocabulary.csv Day 3 5 TempWord
- Day 3의 Id == 1이 없다면 1부터 시작
- 있으면 마지막 번호 + 1부터 추가
- Word는 "TempWord_{30*(day-1) + Id}" 형식으로 생성
"""

import csv
import sys
import os

def add_rows_to_day(csv_file, day_value, num_rows, word_value=None):
    """
    특정 Day에 행을 추가
    
    Args:
        csv_file: CSV 파일 경로
        day_value: Day 값 (문자열 또는 숫자)
        num_rows: 추가할 행 수
        word_value: Word 값 (사용하지 않음, TempWord_{30*(day-1) + Id} 형식 사용)
    """
    # 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # CSV 파일 읽기
    rows = []
    day_rows = []  # 해당 Day의 행들
    other_rows = []  # 다른 Day의 행들
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        if fieldnames is None or 'Id' not in fieldnames or 'Day' not in fieldnames:
            print("오류: CSV 파일에 'Id' 또는 'Day' 컬럼이 없습니다.")
            sys.exit(1)
        
        for row in reader:
            if row['Day'].strip() == str(day_value):
                day_rows.append(row)
            else:
                other_rows.append(row)
    
    # Day 값이 문자열인지 숫자인지 확인
    day_str = str(day_value)
    
    # 해당 Day의 Id 목록 추출 및 정렬
    day_ids = []
    for row in day_rows:
        try:
            day_ids.append(int(row['Id'].strip()))
        except ValueError:
            continue
    
    # 시작 Id 결정
    if len(day_ids) == 0:
        # Day에 행이 없으면 1부터 시작
        start_id = 1
    else:
        # Id == 1이 있는지 확인
        if 1 in day_ids:
            # 마지막 번호 + 1부터 시작
            start_id = max(day_ids) + 1
        else:
            # Id == 1이 없으면 1부터 시작
            start_id = 1
    
    # 새 행 생성
    new_rows = []
    day_int = int(day_value)
    for i in range(num_rows):
        new_id = start_id + i
        # TempWord_{30*(day-1) + Id} 형식으로 생성
        word_name = f"TempWord_{30 * (day_int - 1) + new_id}"
        new_row = {
            'Id': str(new_id),
            'Word': word_name,
            'Day': day_str
        }
        new_rows.append(new_row)
    
    # 모든 행 합치기 (다른 Day 행들 + 기존 Day 행들 + 새 행들)
    all_rows = other_rows + day_rows + new_rows
    
    # CSV 파일에 쓰기
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"처리 완료!")
    print(f"  Day {day_value}: {len(day_rows)}개 기존 행, {num_rows}개 새 행 추가")
    print(f"  시작 Id: {start_id}")
    print(f"  추가된 Id 범위: {start_id} ~ {start_id + num_rows - 1}")
    if new_rows:
        print(f"  Word 형식: TempWord_{{30*(day-1) + Id}}")
        print(f"  예시: {new_rows[0]['Word']}")

def main():
    if len(sys.argv) < 6:
        print("사용법: python script/tmp/AddRows.py <csv_file> Day <day_value> <num_rows> <word_value>")
        print("예시: python script/tmp/AddRows.py data/Vocabulary.csv Day 3 5 TempWord")    
        word_value = "TempWord"
    else:
        word_value = sys.argv[5]
    csv_file = sys.argv[1]
    day_value = sys.argv[3]  # "Day" 다음 값
    num_rows = int(sys.argv[4])
    
    add_rows_to_day(csv_file, day_value, num_rows, word_value)

if __name__ == "__main__":
    main()
