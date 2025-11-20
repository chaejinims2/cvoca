#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vocabulary_join_Meaning_removed.csv에 MeaningId 컬럼을 추가하는 스크립트
- 기본값: 1
- 같은 VocabularyId가 있으면 1씩 증가하여 부여
사용법: python script/tmp/AddMeaningIdByVocabularyId.py data/Vocabulary_join_Meaning_removed.csv
"""

import csv
import sys
import os

def add_meaning_id_by_vocabulary_id(csv_file):
    """
    MeaningId 컬럼을 추가하고 VocabularyId별로 1부터 증가하여 부여
    
    Args:
        csv_file: CSV 파일 경로
    """
    # 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # CSV 파일 읽기
    rows = []
    vocab_counter = {}  # VocabularyId별 카운터
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None:
            print("오류: CSV 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        if 'VocabularyId' not in fieldnames:
            print("오류: CSV 파일에 'VocabularyId' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        # MeaningId 컬럼이 이미 있는지 확인
        if 'MeaningId' in fieldnames:
            print("경고: 'MeaningId' 컬럼이 이미 존재합니다. 기존 값을 덮어씁니다.")
        else:
            # VocabularyId 다음에 MeaningId 컬럼 추가
            vocab_id_index = fieldnames.index('VocabularyId')
            fieldnames.insert(vocab_id_index + 1, 'MeaningId')
            print("'MeaningId' 컬럼을 추가합니다.")
        
        for row in reader:
            vocabulary_id = row['VocabularyId'].strip()
            
            # VocabularyId별 카운터 초기화 또는 증가
            if vocabulary_id not in vocab_counter:
                vocab_counter[vocabulary_id] = 0
            
            vocab_counter[vocabulary_id] += 1
            meaning_id = vocab_counter[vocabulary_id]
            
            # MeaningId 설정
            row['MeaningId'] = str(meaning_id)
            rows.append(row)
    
    # CSV 파일에 쓰기
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # 통계 출력
    multi_meaning_count = sum(1 for count in vocab_counter.values() if count > 1)
    max_meanings = max(vocab_counter.values()) if vocab_counter else 0
    
    print(f"처리 완료!")
    print(f"  파일: {csv_file}")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")
    print(f"  총 VocabularyId 수: {len(vocab_counter)}개")
    print(f"  여러 의미를 가진 VocabularyId: {multi_meaning_count}개")
    print(f"  최대 의미 개수: {max_meanings}개")
    
    # 예시 출력
    if rows:
        print(f"\n  예시:")
        example_vocab_id = None
        for vocab_id, count in vocab_counter.items():
            if count > 1:
                example_vocab_id = vocab_id
                break
        
        if example_vocab_id:
            print(f"  VocabularyId {example_vocab_id}의 의미들:")
            for row in rows:
                if row['VocabularyId'].strip() == example_vocab_id:
                    print(f"    MeaningId={row['MeaningId']}, definition={row.get('definition', '')[:30]}...")

def main():
    if len(sys.argv) < 2:
        print("사용법: python script/tmp/AddMeaningIdByVocabularyId.py <csv_file>")
        print("예시: python script/tmp/AddMeaningIdByVocabularyId.py data/Vocabulary_join_Meaning_removed.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    add_meaning_id_by_vocabulary_id(csv_file)

if __name__ == "__main__":
    main()

