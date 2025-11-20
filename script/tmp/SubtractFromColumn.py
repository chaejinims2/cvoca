#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일의 특정 컬럼 값에서 N을 빼는 스크립트
사용법: python script/tmp/SubtractFromColumn.py <input_file> <column_name> <N> [output_file]
예시: python script/tmp/SubtractFromColumn.py data/Meaning_removed.csv sense_no 1000
"""

import csv
import sys
import os

def subtract_from_column(input_file, column_name, subtract_value, output_file=None):
    """
    CSV 파일의 특정 컬럼 값에서 N을 빼기
    
    Args:
        input_file: 입력 CSV 파일 경로
        column_name: 값을 빼줄 컬럼명
        subtract_value: 빼줄 값 (N)
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일 덮어쓰기)
    """
    # 파일 존재 확인
    if not os.path.exists(input_file):
        print(f"오류: CSV 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if output_file is None:
        output_file = input_file
    
    rows = []
    updated_count = 0
    error_count = 0
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None:
            print("오류: CSV 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        # 컬럼 존재 확인
        if column_name not in fieldnames:
            print(f"오류: CSV 파일에 '{column_name}' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        for row in reader:
            try:
                # 현재 값 가져오기
                current_value = row[column_name].strip()
                
                # 빈 값이면 스킵
                if not current_value or current_value.lower() == 'null':
                    rows.append(row)
                    continue
                
                # 숫자로 변환
                try:
                    numeric_value = float(current_value)
                    new_value = numeric_value - subtract_value
                    
                    # 정수인 경우 정수로 저장
                    if numeric_value == int(numeric_value) and subtract_value == int(subtract_value):
                        new_row = row.copy()
                        new_row[column_name] = str(int(new_value))
                    else:
                        new_row = row.copy()
                        new_row[column_name] = str(new_value)
                    
                    rows.append(new_row)
                    updated_count += 1
                    
                except ValueError:
                    # 숫자가 아닌 경우 원본 유지
                    print(f"경고: '{current_value}'는 숫자가 아닙니다. 원본 유지합니다.")
                    rows.append(row)
                    error_count += 1
                    
            except Exception as e:
                print(f"경고: 행 처리 중 오류 발생: {e}")
                rows.append(row)
                error_count += 1
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  컬럼: {column_name}")
    print(f"  빼는 값: {subtract_value}")
    print(f"  업데이트된 행: {updated_count}개")
    if error_count > 0:
        print(f"  오류 발생 행: {error_count}개")
    
    if rows and updated_count > 0:
        # 첫 번째 업데이트된 행의 예시 출력
        for row in rows:
            if row[column_name] and row[column_name].strip():
                try:
                    val = float(row[column_name])
                    print(f"  예시: {column_name} = {val}")
                    break
                except:
                    pass

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("사용법: python script/tmp/SubtractFromColumn.py <input_file> <column_name> <N> [output_file]")
        print("예시: python script/tmp/SubtractFromColumn.py data/Meaning_removed.csv sense_no 1000")
        print("예시: python script/tmp/SubtractFromColumn.py data/file.csv ColumnName 50 output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    column_name = sys.argv[2]
    
    try:
        subtract_value = float(sys.argv[3])
    except ValueError:
        print(f"오류: '{sys.argv[3]}'는 유효한 숫자가 아닙니다.")
        sys.exit(1)
    
    output_file = sys.argv[4] if len(sys.argv) > 4 else None
    
    subtract_from_column(input_file, column_name, subtract_value, output_file)

