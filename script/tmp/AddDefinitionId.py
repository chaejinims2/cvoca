#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meaning_removed.csv에 definition_id 컬럼을 추가하는 스크립트
definition_id = word_id * 10 + sense_no
사용법: python script/tmp/AddDefinitionId.py [input_file] [output_file]
"""

import csv
import sys
import os

def add_definition_id(input_file, output_file=None):
    """
    definition_id 컬럼을 추가하고 word_id와 sense_no를 조합하여 생성
    definition_id = word_id * 10 + sense_no
    
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
    
    rows = []
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None:
            print("오류: CSV 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        # word_id와 sense_no 컬럼 확인
        if 'word_id' not in fieldnames:
            print("오류: CSV 파일에 'word_id' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        if 'sense_no' not in fieldnames:
            print("오류: CSV 파일에 'sense_no' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        # definition_id 컬럼이 이미 있으면 경고
        if 'definition_id' in fieldnames:
            print("경고: 'definition_id' 컬럼이 이미 존재합니다. 기존 값을 덮어씁니다.")
        
        # definition_id 컬럼 추가 (기존 컬럼 순서 유지)
        if 'definition_id' not in fieldnames:
            fieldnames.append('definition_id')
        
        for row in reader:
            try:
                word_id = int(row['word_id'])
                sense_no = int(row['sense_no']) if row['sense_no'] and row['sense_no'].lower() != 'null' else 0
                
                # definition_id = word_id * 10 + sense_no
                definition_id = word_id * 10 + sense_no
                
                new_row = row.copy()
                new_row['definition_id'] = str(definition_id)
                rows.append(new_row)
                
            except ValueError as e:
                print(f"경고: 행 처리 중 오류 발생 (word_id={row.get('word_id')}, sense_no={row.get('sense_no')}): {e}")
                # 오류가 있어도 definition_id를 0으로 설정하고 계속 진행
                new_row = row.copy()
                new_row['definition_id'] = '0'
                rows.append(new_row)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  처리된 행: {len(rows)}개")
    print(f"  definition_id 계산식: word_id * 10 + sense_no")
    if rows:
        print(f"  예시: word_id={rows[0]['word_id']}, sense_no={rows[0]['sense_no']} → definition_id={rows[0]['definition_id']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/tmp/AddDefinitionId.py <input_file> [output_file]")
        print("예시: python script/tmp/AddDefinitionId.py data/definitions/13.csv")
        print("      python script/tmp/AddDefinitionId.py data/definitions/13.csv output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    add_definition_id(input_file, output_file)

