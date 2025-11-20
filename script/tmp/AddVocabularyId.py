#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vocabulary.csv에 VocabularyId 컬럼을 추가하는 스크립트
VocabularyId = 30*(day-1) + Id
사용법: python script/tmp/AddVocabularyId.py data/Vocabulary.csv
"""

import csv
import sys
import os

def add_vocabulary_id(csv_file):
    """
    Vocabulary.csv에 VocabularyId 컬럼 추가
    VocabularyId = 30*(day-1) + Id
    
    Args:
        csv_file: CSV 파일 경로
    """
    # 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # CSV 파일 읽기
    rows = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None or 'Id' not in fieldnames or 'Day' not in fieldnames:
            print("오류: CSV 파일에 'Id' 또는 'Day' 컬럼이 없습니다.")
            sys.exit(1)
        
        # VocabularyId 컬럼이 이미 있는지 확인
        if 'VocabularyId' in fieldnames:
            print("경고: 'VocabularyId' 컬럼이 이미 존재합니다. 기존 값을 덮어씁니다.")
        else:
            # Id 다음에 VocabularyId 컬럼 추가
            id_index = fieldnames.index('Id')
            fieldnames.insert(id_index + 1, 'VocabularyId')
            print("'VocabularyId' 컬럼을 추가합니다.")
        
        for row in reader:
            try:
                day = int(row['Day'].strip())
                vocab_id = int(row['Id'].strip())
                # VocabularyId = 30*(day-1) + Id 계산
                vocabulary_id = 30 * (day - 1) + vocab_id
                row['VocabularyId'] = str(vocabulary_id)
            except ValueError as e:
                print(f"경고: 행을 처리하는 중 오류 발생 (Day={row.get('Day')}, Id={row.get('Id')}): {e}")
                row['VocabularyId'] = ''
            
            rows.append(row)
    
    # CSV 파일에 쓰기
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  파일: {csv_file}")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")
    if rows:
        print(f"  예시: Day={rows[0].get('Day')}, Id={rows[0].get('Id')}, VocabularyId={rows[0].get('VocabularyId')}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python script/tmp/AddVocabularyId.py <csv_file>")
        print("예시: python script/tmp/AddVocabularyId.py data/Vocabulary.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    add_vocabulary_id(csv_file)

if __name__ == "__main__":
    main()

