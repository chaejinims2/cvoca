#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vocabulary_Meaning_Example_sorted.csv의 MeaningId를 MeaningId - VocabularyId로 계산하여 변경
사용법: python script/tmp/UpdateMeaningIdFormat.py data/Vocabulary_Meaning_Example_sorted.csv
"""

import csv
import sys
import os

def update_meaning_id_format(csv_file):
    """
    MeaningId를 MeaningId - VocabularyId로 계산하여 변경
    
    Args:
        csv_file: CSV 파일 경로
    """
    # 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # CSV 파일 읽기
    rows = []
    updated_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None:
            print("오류: CSV 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        if 'MeaningId' not in fieldnames:
            print("오류: CSV 파일에 'MeaningId' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        if 'VocabularyId' not in fieldnames:
            print("오류: CSV 파일에 'VocabularyId' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        for row in reader:
            meaning_id_str = row['MeaningId'].strip()
            vocabulary_id_str = row['VocabularyId'].strip()
            
            # MeaningId와 VocabularyId가 모두 있는 경우에만 변경
            if meaning_id_str and vocabulary_id_str:
                try:
                    # 숫자로 변환하여 계산
                    meaning_id = int(meaning_id_str)
                    vocabulary_id = int(vocabulary_id_str)
                    # MeaningId - VocabularyId 계산
                    new_meaning_id = meaning_id - vocabulary_id
                    row['MeaningId'] = str(new_meaning_id)
                    updated_count += 1
                except ValueError:
                    # 숫자로 변환할 수 없으면 그대로 유지
                    print(f"경고: MeaningId='{meaning_id_str}' 또는 VocabularyId='{vocabulary_id_str}'를 숫자로 변환할 수 없습니다. 건너뜁니다.")
            else:
                # 값이 없으면 그대로 유지
                pass
            
            rows.append(row)
    
    # CSV 파일에 쓰기
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  파일: {csv_file}")
    print(f"  업데이트된 행 수: {updated_count}개")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")
    
    # 예시 출력
    if rows:
        print(f"\n  예시:")
        for i, row in enumerate(rows[:5]):
            if row.get('MeaningId') and row.get('VocabularyId'):
                print(f"    MeaningId={row['MeaningId']}, VocabularyId={row['VocabularyId']}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python script/tmp/UpdateMeaningIdFormat.py <csv_file>")
        print("예시: python script/tmp/UpdateMeaningIdFormat.py data/Vocabulary_Meaning_Example_sorted.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    update_meaning_id_format(csv_file)

if __name__ == "__main__":
    main()

