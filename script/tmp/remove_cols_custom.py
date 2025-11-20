#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일에서 지정한 컬럼들을 제거하는 스크립트
사용법: python script/remove_columns.py --overwrite <input_file> <column1> <column2> ... [output_file]
"""

import csv
import sys
import os

def remove_columns(input_file, columns_to_remove, output_file=None, overwrite=False):
    """
    CSV 파일에서 지정한 컬럼들을 제거
    
    Args:
        input_file: 입력 CSV 파일 경로
        columns_to_remove: 제거할 컬럼명 리스트
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일명에 _removed 추가)
    """
    if not os.path.exists(input_file):
        print(f"오류: 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if output_file is None and not overwrite:
        base_name = os.path.splitext(input_file)[0]
        ext = os.path.splitext(input_file)[1]
        output_file = f"{base_name}_removed{ext}"
    
    if overwrite:
        output_file = input_file
    
    rows = []
    removed_columns = []
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # 제거할 컬럼 확인
        for col in columns_to_remove:
            if col in fieldnames:
                removed_columns.append(col)
            else:
                print(f"경고: 컬럼 '{col}'이 파일에 존재하지 않습니다.")
        
        if not removed_columns:
            print("오류: 제거할 컬럼이 없습니다.")
            sys.exit(1)
        
        # 남을 컬럼 목록
        remaining_columns = [col for col in fieldnames if col not in removed_columns]
        
        print(f"제거할 컬럼: {', '.join(removed_columns)}")
        print(f"남을 컬럼: {', '.join(remaining_columns)}")
        
        for row in reader:
            # 제거할 컬럼을 제외한 새 행 생성
            new_row = {col: row[col] for col in remaining_columns}
            rows.append(new_row)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=remaining_columns)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")
    print(f"  제거된 컬럼: {len(removed_columns)}개")
    print(f"  남은 컬럼: {len(remaining_columns)}개")

if __name__ == "__main__":
    # --overwrite 옵션 확인 및 제거
    overwrite = '--overwrite' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != '--overwrite']
    
    if len(args) < 2:
        print("사용법:")
        print("  python script/tmp/remove_cols_custom.py <input_file> <column1> [column2] ... [output_file]")
        print("  python script/tmp/remove_cols_custom.py --overwrite <input_file> <column1> [column2] ...")
        print("\n예시:")
        print("  python script/tmp/remove_cols_custom.py data.csv \"Day\" \"Multi-select\"")
        print("  python script/tmp/remove_cols_custom.py data.csv \"Day\" \"Multi-select\" output.csv")
        print("  python script/tmp/remove_cols_custom.py --overwrite data.csv \"Day\" \"Multi-select\"")
        print("      (컬럼명에 공백이 있으면 따옴표로 감싸주세요)")
        sys.exit(1)

    input_file = args[0]
    
    # 마지막 인자가 .csv 파일이고 입력 파일과 다르면 출력 파일로 간주
    output_file = None
    columns_to_remove = []
    
    for i, arg in enumerate(args[1:], 1):
        # 마지막 인자이고 .csv로 끝나고 입력 파일과 다르면 출력 파일
        if i == len(args) - 1 and arg.endswith('.csv') and arg != input_file:
            output_file = arg
        else:
            columns_to_remove.append(arg)
    
    if not columns_to_remove:
        print("오류: 제거할 컬럼을 최소 1개 이상 지정해야 합니다.")
        sys.exit(1)
    
    if overwrite:
        output_file = input_file
    
    remove_columns(input_file, columns_to_remove, output_file, overwrite)

