#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일의 행들을 지정한 컬럼 기준으로 우선순위 정렬하는 스크립트
사용법: python script/sort_rows_by_col.py [+column1] [-column2] ...
예시: python script/sort_rows_by_col.py +Id -Word
      (+는 오름차순, -는 내림차순)
"""

import csv
import sys
import os

def parse_sort_columns(args):
    """
    정렬 컬럼 인자 파싱
    
    Args:
        args: 정렬 컬럼 인자 리스트 (예: ['+Id', '-Word'])
        
    Returns:
        정렬 컬럼 리스트 [(column_name, reverse), ...]
    """
    sort_columns = []
    
    for arg in args:
        if not arg.startswith(('+', '-')):
            print(f"경고: '{arg}'는 무시됩니다. 컬럼명은 + 또는 -로 시작해야 합니다.")
            continue
        
        reverse = arg.startswith('-')
        column_name = arg[1:]  # + 또는 - 제거
        
        if not column_name:
            print(f"경고: '{arg}'는 유효한 컬럼명이 아닙니다.")
            continue
        
        sort_columns.append((column_name, reverse))
    
    return sort_columns

def sort_rows_by_columns(input_file, sort_columns, output_file=None):
    """
    CSV 파일의 행들을 지정한 컬럼 기준으로 우선순위 정렬
    
    Args:
        input_file: 입력 CSV 파일 경로
        sort_columns: 정렬 컬럼 리스트 [(column_name, reverse), ...]
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일명에 _sorted 추가)
    """
    if not os.path.exists(input_file):
        print(f"오류: 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if not sort_columns:
        print("오류: 정렬 기준 컬럼이 지정되지 않았습니다.")
        sys.exit(1)
    
    if output_file is None:
        # 입력 파일의 디렉토리에 output 폴더 생성
        input_dir = os.path.dirname(os.path.abspath(input_file))
        output_dir = os.path.join(input_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.basename(os.path.splitext(input_file)[0])
        ext = os.path.splitext(input_file)[1]
        output_file = os.path.join(output_dir, f"{base_name}_sorted{ext}")
    
    rows = []
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # 정렬 기준 컬럼이 모두 있는지 확인
        for column_name, _ in sort_columns:
            if column_name not in fieldnames:
                print(f"오류: CSV 파일에 '{column_name}' 컬럼이 없습니다.")
                print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
                sys.exit(1)
        
        for row in reader:
            rows.append(row)
    
    # 정렬 키 함수 생성
    def get_sort_key(row):
        """
        각 정렬 컬럼에 대한 정렬 키 생성
        숫자로 변환 가능하면 숫자로, 아니면 문자열로 비교
        """
        keys = []
        for column_name, reverse in sort_columns:
            value = row.get(column_name, '').strip()
            
            if not value:
                # 빈 값은 맨 뒤로 (내림차순이면 맨 앞으로)
                if reverse:
                    keys.append((1, 'zzz'))  # 내림차순: 빈 값이 맨 앞
                else:
                    keys.append((1, ''))  # 오름차순: 빈 값이 맨 뒤
                continue
            
            # 숫자로 변환 시도
            try:
                num_value = int(value)
                if reverse:
                    keys.append((0, -num_value))  # 내림차순: 음수로 변환
                else:
                    keys.append((0, num_value))  # 오름차순
            except ValueError:
                try:
                    num_value = float(value)
                    if reverse:
                        keys.append((0, -num_value))  # 내림차순: 음수로 변환
                    else:
                        keys.append((0, num_value))  # 오름차순
                except ValueError:
                    # 문자열로 비교
                    if reverse:
                        # 내림차순: 문자열을 역순으로 비교하기 위해 각 문자를 음수로 변환
                        # 또는 더 간단하게: 문자열을 역순으로 변환
                        keys.append((0, tuple(-ord(c) for c in value)))
                    else:
                        keys.append((0, value))  # 오름차순
        
        return tuple(keys)
    
    # 정렬 수행
    sorted_rows = sorted(rows, key=get_sort_key)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  정렬 기준:")
    for i, (column_name, reverse) in enumerate(sort_columns, 1):
        direction = "내림차순" if reverse else "오름차순"
        print(f"    {i}. {column_name} ({direction})")
    print(f"  총 행 수: {len(sorted_rows)}개 (헤더 제외)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/sort_rows_by_col.py <input_file> [+column1] [-column2] ... [output_file]")
        print("예시: python script/sort_rows_by_col.py file.csv +Id -Word")
        print("      python script/sort_rows_by_col.py file.csv +Id -Word output.csv")
        print("      (+는 오름차순, -는 내림차순)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 정렬 컬럼 인자와 출력 파일명 분리
    sort_args = []
    output_file = None
    
    for arg in sys.argv[2:]:
        if arg.startswith(('+', '-')):
            sort_args.append(arg)
        elif arg.endswith('.csv'):
            output_file = arg
        else:
            print(f"경고: '{arg}'는 무시됩니다.")
    
    if not sort_args:
        print("오류: 정렬 기준 컬럼이 지정되지 않았습니다.")
        print("      컬럼명은 + 또는 -로 시작해야 합니다.")
        sys.exit(1)
    
    # 정렬 컬럼 파싱
    sort_columns = parse_sort_columns(sort_args)
    
    sort_rows_by_columns(input_file, sort_columns, output_file)

