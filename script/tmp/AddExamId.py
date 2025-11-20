#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exams.csv에 ExamId 컬럼을 추가하는 스크립트
ExamId = sense_no * 10 + example_no
사용법: python script/tmp/AddExamId.py [input_file] [output_file]
"""

import csv
import sys
import os

def add_exam_id(input_file, output_file=None):
    """
    ExamId 컬럼을 추가하고 MeanId와 UseId를 조합하여 생성
    
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
        
        # MeanId와 example_no 컬럼 확인
        if 'sense_no' not in fieldnames:
            print("오류: CSV 파일에 'sense_no' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        if 'example_no' not in fieldnames:
            print("오류: CSV 파일에 'example_no' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        # ExamId 컬럼이 이미 있으면 경고
        if 'ExamId' in fieldnames:
            print("경고: 'ExamId' 컬럼이 이미 존재합니다. 기존 값을 덮어씁니다.")
        
        # ExamId를 첫 번째 컬럼으로 추가
        new_fieldnames = ['ExamId'] + [col for col in fieldnames if col != 'ExamId']
        
        for row in reader:
            try:
                mean_id = int(row['sense_no']) if row['sense_no'] and row['sense_no'].lower() != 'null' else 0
                use_id = int(row['example_no']) if row['example_no'] and row['example_no'].lower() != 'null' else 0
                
                # ExamId = sense_no * 10 + example_no
                exam_id = mean_id * 10 + use_id
                
                new_row = row.copy()
                new_row['ExamId'] = str(exam_id)
                rows.append(new_row)
                
            except ValueError as e:
                print(f"경고: 행 처리 중 오류 발생 (sense_no={row.get('sense_no')}, example_no={row.get('example_no')}): {e}")
                # 오류가 있어도 ExamId를 0으로 설정하고 계속 진행
                new_row = row.copy()
                new_row['ExamId'] = '0'
                rows.append(new_row)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  처리된 행: {len(rows)}개")
    print(f"  ExamId 형식: sense_no * 10 + example_no")
    if rows:
        print(f"  예시: sense_no={rows[0]['sense_no']}, example_no={rows[0]['example_no']} → ExamId={rows[0]['ExamId']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/tmp/AddExamId.py <input_file> [output_file]")
        print("예시: python script/tmp/AddExamId.py data/new/Exams.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    add_exam_id(input_file, output_file)

