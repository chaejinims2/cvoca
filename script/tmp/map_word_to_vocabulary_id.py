#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일의 Word 컬럼을 VocabularyId로 매핑하여 대체하는 스크립트
사용법: python script/map_word_to_vocabulary_id.py <input_file> <db_file> [output_file]
"""

import csv
import sqlite3
import sys
import os

def map_word_to_vocabulary_id(input_file, db_file, output_file=None):
    """
    CSV 파일의 Word 컬럼을 Vocabulary 테이블에서 찾아 VocabularyId로 대체
    
    Args:
        input_file: 입력 CSV 파일 경로
        db_file: SQLite 데이터베이스 파일 경로
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일명에 _mapped 추가)
    """
    if not os.path.exists(input_file):
        print(f"오류: 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        ext = os.path.splitext(input_file)[1]
        output_file = f"{base_name}_mapped{ext}"
    
    # 데이터베이스 연결
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Vocabulary 테이블에서 Word -> Id 매핑 딕셔너리 생성
    cursor.execute("SELECT Word, Id FROM Vocabulary")
    word_to_id = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"Vocabulary 테이블에서 {len(word_to_id)}개의 단어를 로드했습니다.")
    
    rows = []
    mapped_count = 0
    not_found_count = 0
    not_found_words = []
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # Word 컬럼이 있는지 확인
        if 'Word' not in fieldnames:
            print(f"오류: CSV 파일에 'Word' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            conn.close()
            sys.exit(1)
        
        # VocabularyId 컬럼이 이미 있으면 경고
        if 'VocabularyId' in fieldnames:
            print("경고: 'VocabularyId' 컬럼이 이미 존재합니다. 기존 컬럼을 덮어씁니다.")
        else:
            # Word 다음에 VocabularyId 삽입
            word_index = fieldnames.index('Word')
            fieldnames.insert(word_index + 1, 'VocabularyId')
        
        for row in reader:
            word = row.get('Word', '').strip()
            
            if not word:
                # Word가 비어있으면 VocabularyId도 비워둠
                row['VocabularyId'] = ''
                rows.append(row)
                continue
            
            # Word를 VocabularyId로 매핑
            if word in word_to_id:
                row['VocabularyId'] = str(word_to_id[word])
                mapped_count += 1
            else:
                # 매핑 실패
                row['VocabularyId'] = ''
                not_found_count += 1
                if word not in not_found_words:
                    not_found_words.append(word)
                print(f"경고: '{word}'에 해당하는 VocabularyId를 찾을 수 없습니다.")
            
            rows.append(row)
    
    conn.close()
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  총 행 수: {len(rows)}개")
    print(f"  매핑 성공: {mapped_count}개")
    print(f"  매핑 실패: {not_found_count}개")
    if not_found_words:
        print(f"  찾을 수 없는 단어: {', '.join(not_found_words[:10])}")
        if len(not_found_words) > 10:
            print(f"  ... 외 {len(not_found_words) - 10}개")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python script/map_word_to_vocabulary_id.py <input_file> <db_file> [output_file]")
        print("예시: python script/map_word_to_vocabulary_id.py alll_cleaned.csv data/vocabulary.db")
        sys.exit(1)
    
    input_file = sys.argv[1]
    db_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    map_word_to_vocabulary_id(input_file, db_file, output_file)

