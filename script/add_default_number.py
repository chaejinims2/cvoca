#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일의 각 행에 순서대로 숫자를 부여하는 스크립트
지정한 컬럼명이 없으면 추가하고, 있으면 덮어씁니다.
사용법: python script/add_default_number.py <input_file> <column_name> [output_file] [start_number]
"""

import csv
import sys
import os

def add_default_number(input_file, column_name, output_file=None, start_number=1, force=False):
    """
    CSV 파일의 각 행에 순서대로 숫자를 부여
    
    Args:
        input_file: 입력 CSV 파일 경로
        column_name: 숫자를 부여할 컬럼명
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일명에 _numbered 추가)
        start_number: 시작 번호 (기본값: 1)
        force: 컬럼이 이미 존재할 때 덮어쓸지 여부
    """
    if not os.path.exists(input_file):
        print(f"오류: 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if output_file is None:
        # 입력 파일의 디렉토리에 output 폴더 생성
        input_dir = os.path.dirname(os.path.abspath(input_file))
        output_dir = os.path.join(input_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.basename(os.path.splitext(input_file)[0])
        ext = os.path.splitext(input_file)[1]
        output_file = os.path.join(output_dir, f"{base_name}_numbered{ext}")
    
    rows = []
    current_number = start_number
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # 지정한 컬럼이 있는지 확인
        if column_name in fieldnames:
            if force:
                print(f"경고: '{column_name}' 컬럼이 이미 존재합니다. 기존 값을 덮어씁니다.")
                # 컬럼을 맨 앞으로 이동
                fieldnames.remove(column_name)
                fieldnames.insert(0, column_name)
            else:
                print(f"오류: '{column_name}' 컬럼이 이미 존재합니다.")
                print("      덮어쓰려면 -rf 옵션을 사용하세요.")
                sys.exit(1)
        else:
            # 컬럼을 맨 앞에 추가
            print(f"'{column_name}' 컬럼이 없습니다. 새로 추가합니다.")
            fieldnames.insert(0, column_name)
        
        for row in reader:
            # 숫자 부여
            row[column_name] = str(current_number)
            current_number += 1
            rows.append(row)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  컬럼명: {column_name}")
    print(f"  시작 번호: {start_number}")
    print(f"  마지막 번호: {current_number - 1}")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python script/add_default_number.py <input_file> <column_name> [-rf] [output_file] [start_number]")
        print("예시: python script/add_default_number.py file.csv UniqueColId")
        print("      python script/add_default_number.py file.csv UniqueColId -rf")
        print("      python script/add_default_number.py file.csv UniqueColId output.csv")
        print("      python script/add_default_number.py file.csv UniqueColId -rf output.csv 100")
        print("      (-rf 옵션: 컬럼이 이미 존재할 때 덮어씁니다)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    column_name = sys.argv[2]
    force = '-rf' in sys.argv
    
    # 출력 파일과 시작 번호 파싱 (-rf 제외)
    args_without_rf = [arg for arg in sys.argv[3:] if arg != '-rf']
    
    output_file = None
    start_number = 1
    
    if len(args_without_rf) > 0:
        # 첫 번째 인자가 .csv로 끝나면 출력 파일명
        if args_without_rf[0].endswith('.csv'):
            output_file = args_without_rf[0]
            # 두 번째 인자가 있으면 시작 번호
            if len(args_without_rf) > 1:
                try:
                    start_number = int(args_without_rf[1])
                except ValueError:
                    print(f"경고: 시작 번호 '{args_without_rf[1]}'를 숫자로 변환할 수 없습니다. 기본값 1을 사용합니다.")
        else:
            # 첫 번째 인자가 숫자면 시작 번호
            try:
                start_number = int(args_without_rf[0])
            except ValueError:
                print(f"경고: 시작 번호 '{args_without_rf[0]}'를 숫자로 변환할 수 없습니다. 기본값 1을 사용합니다.")
    
    add_default_number(input_file, column_name, output_file, start_number, force)

