#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
두 CSV 파일을 비교해서 다른 행들을 탐지하는 스크립트
사용법: python script/compare_csv.py <file1.csv> <file2.csv> [key_column] [output_file]
"""

import csv
import sys
import os

def compare_csv_files(file1, file2, key_column=None, output_file=None):
    """
    두 CSV 파일을 비교해서 다른 행들을 탐지
    
    Args:
        file1: 첫 번째 CSV 파일 경로
        file2: 두 번째 CSV 파일 경로
        key_column: 비교에 사용할 키 컬럼명 (None이면 전체 행 비교)
        output_file: 결과를 저장할 파일 경로 (None이면 출력만)
    """
    if not os.path.exists(file1):
        print(f"오류: 파일 '{file1}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if not os.path.exists(file2):
        print(f"오류: 파일 '{file2}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 첫 번째 파일 읽기
    rows1 = {}
    fieldnames1 = None
    
    with open(file1, 'r', encoding='utf-8') as f1:
        reader1 = csv.DictReader(f1)
        fieldnames1 = list(reader1.fieldnames)
        
        if key_column:
            if key_column not in fieldnames1:
                print(f"오류: '{file1}'에 '{key_column}' 컬럼이 없습니다.")
                sys.exit(1)
            for row in reader1:
                key = row[key_column]
                rows1[key] = row
        else:
            # 전체 행을 문자열로 변환하여 키로 사용
            for idx, row in enumerate(reader1):
                rows1[idx] = row
    
    # 두 번째 파일 읽기
    rows2 = {}
    fieldnames2 = None
    
    with open(file2, 'r', encoding='utf-8') as f2:
        reader2 = csv.DictReader(f2)
        fieldnames2 = list(reader2.fieldnames)
        
        if key_column:
            if key_column not in fieldnames2:
                print(f"오류: '{file2}'에 '{key_column}' 컬럼이 없습니다.")
                sys.exit(1)
            for row in reader2:
                key = row[key_column]
                rows2[key] = row
        else:
            # 전체 행을 문자열로 변환하여 키로 사용
            for idx, row in enumerate(reader2):
                rows2[idx] = row
    
    # 공통 컬럼 찾기
    common_columns = set(fieldnames1) & set(fieldnames2)
    if not common_columns:
        print("경고: 두 파일에 공통 컬럼이 없습니다.")
    
    # 비교 결과
    only_in_file1 = []
    only_in_file2 = []
    different_rows = []
    
    if key_column:
        # 키 컬럼 기준 비교
        keys1 = set(rows1.keys())
        keys2 = set(rows2.keys())
        
        # file1에만 있는 키
        only_keys1 = keys1 - keys2
        for key in only_keys1:
            only_in_file1.append(rows1[key])
        
        # file2에만 있는 키
        only_keys2 = keys2 - keys1
        for key in only_keys2:
            only_in_file2.append(rows2[key])
        
        # 양쪽에 있지만 다른 행
        common_keys = keys1 & keys2
        for key in common_keys:
            row1 = rows1[key]
            row2 = rows2[key]
            
            # 공통 컬럼만 비교
            different = False
            diff_details = {}
            for col in common_columns:
                val1 = row1.get(col, '').strip()
                val2 = row2.get(col, '').strip()
                if val1 != val2:
                    different = True
                    diff_details[col] = {'file1': val1, 'file2': val2}
            
            if different:
                different_rows.append({
                    'key': key,
                    'row1': row1,
                    'row2': row2,
                    'differences': diff_details
                })
    else:
        # 인덱스 기준 비교 (행 수가 다를 수 있음)
        max_idx = max(len(rows1), len(rows2))
        
        for idx in range(max_idx):
            if idx in rows1 and idx not in rows2:
                only_in_file1.append(rows1[idx])
            elif idx in rows2 and idx not in rows1:
                only_in_file2.append(rows2[idx])
            elif idx in rows1 and idx in rows2:
                row1 = rows1[idx]
                row2 = rows2[idx]
                
                # 공통 컬럼만 비교
                different = False
                diff_details = {}
                for col in common_columns:
                    val1 = row1.get(col, '').strip()
                    val2 = row2.get(col, '').strip()
                    if val1 != val2:
                        different = True
                        diff_details[col] = {'file1': val1, 'file2': val2}
                
                if different:
                    different_rows.append({
                        'index': idx,
                        'row1': row1,
                        'row2': row2,
                        'differences': diff_details
                    })
    
    # 결과 출력
    print(f"\n비교 결과:")
    print(f"  파일1: {file1}")
    print(f"  파일2: {file2}")
    if key_column:
        print(f"  키 컬럼: {key_column}")
    print(f"\n통계:")
    print(f"  파일1에만 있는 행: {len(only_in_file1)}개")
    print(f"  파일2에만 있는 행: {len(only_in_file2)}개")
    print(f"  다른 행: {len(different_rows)}개")
    
    # 다른 행 상세 출력
    if different_rows:
        print(f"\n다른 행 상세:")
        for i, diff in enumerate(different_rows[:10], 1):  # 최대 10개만 출력
            if key_column:
                print(f"\n  [{i}] 키: {diff['key']}")
            else:
                print(f"\n  [{i}] 인덱스: {diff['index']}")
            
            for col, vals in diff['differences'].items():
                print(f"    {col}:")
                print(f"      파일1: {vals['file1']}")
                print(f"      파일2: {vals['file2']}")
        
        if len(different_rows) > 10:
            print(f"\n  ... 외 {len(different_rows) - 10}개")
    
    # 결과를 파일로 저장
    if output_file:
        # 입력 파일의 디렉토리에 output 폴더 생성
        input_dir = os.path.dirname(os.path.abspath(file1))
        output_dir = os.path.join(input_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # output_file이 상대 경로면 output 폴더에 저장
        if not os.path.isabs(output_file):
            output_file = os.path.join(output_dir, os.path.basename(output_file))
        
        with open(output_file, 'w', encoding='utf-8', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(['구분', '키/인덱스', '컬럼', '파일1 값', '파일2 값'])
            
            for diff in different_rows:
                key = diff.get('key', diff.get('index', ''))
                for col, vals in diff['differences'].items():
                    writer.writerow(['다름', key, col, vals['file1'], vals['file2']])
            
            for row in only_in_file1:
                if key_column:
                    key = row[key_column]
                else:
                    key = 'N/A'
                writer.writerow(['파일1에만 있음', key, '전체 행', str(row), ''])
            
            for row in only_in_file2:
                if key_column:
                    key = row[key_column]
                else:
                    key = 'N/A'
                writer.writerow(['파일2에만 있음', key, '전체 행', '', str(row)])
        
        print(f"\n결과가 '{output_file}'에 저장되었습니다.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python script/compare_csv.py <file1.csv> <file2.csv> [key_column] [output_file]")
        print("예시: python script/compare_csv.py file1.csv file2.csv")
        print("      python script/compare_csv.py file1.csv file2.csv Id")
        print("      python script/compare_csv.py file1.csv file2.csv Id diff.csv")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    key_column = None
    output_file = None
    
    if len(sys.argv) > 3:
        # 세 번째 인자가 .csv로 끝나면 출력 파일명
        if sys.argv[3].endswith('.csv'):
            output_file = sys.argv[3]
        else:
            key_column = sys.argv[3]
            # 네 번째 인자가 있으면 출력 파일명
            if len(sys.argv) > 4:
                output_file = sys.argv[4]
    
    compare_csv_files(file1, file2, key_column, output_file)

