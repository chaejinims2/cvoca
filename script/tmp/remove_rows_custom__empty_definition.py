#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일에서 definition 컬럼이 비어있는 행을 제거하는 스크립트
사용법: python script/remove_empty_definition.py <input_file> [output_file]
"""

import csv
import sys
import os

def remove_empty_definition(input_file, output_file=None):
    """
    CSV 파일에서 definition 컬럼이 비어있는 행을 제거
    
    Args:
        input_file: 입력 CSV 파일 경로
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일 덮어쓰기)
    """
    if not os.path.exists(input_file):
        print(f"오류: 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if output_file is None:
        output_file = input_file
    
    rows = []
    removed_count = 0
    kept_count = 0
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # definition 컬럼이 있는지 확인
        if 'definition' not in fieldnames:
            print(f"오류: CSV 파일에 'definition' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        for row in reader:
            definition = row.get('definition', '').strip()
            
            # Definition이 비어있거나 공백만 있으면 제거
            if not definition:
                removed_count += 1
                continue
            
            # Definition이 있으면 유지
            rows.append(row)
            kept_count += 1
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  유지된 행: {kept_count}개")
    print(f"  제거된 행: {removed_count}개")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/remove_empty_definition.py <input_file> [output_file]")
        print("예시: python script/remove_empty_definition.py alll.csv alll_cleaned.csv")
        print("      (output_file을 지정하지 않으면 입력 파일을 덮어씁니다)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    remove_empty_definition(input_file, output_file)

