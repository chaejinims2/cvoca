#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일의 행들을 지정한 컬럼 기준으로 정렬하는 스크립트
사용법: python script/sort_rows_custom.py <input_file> <sort_column> [output_file]
"""

import csv
import sys
import os

def sort_rows_by_column(input_file, sort_column, output_file=None, reverse=False):
    """
    CSV 파일의 행들을 지정한 컬럼 기준으로 정렬
    
    Args:
        input_file: 입력 CSV 파일 경로
        sort_column: 정렬 기준 컬럼명
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일명에 _sorted 추가)
        reverse: 역순 정렬 여부 (기본값: False)
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
        output_file = os.path.join(output_dir, f"{base_name}_sorted{ext}")
    
    rows = []
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # 정렬 기준 컬럼이 있는지 확인
        if sort_column not in fieldnames:
            print(f"오류: CSV 파일에 '{sort_column}' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        for row in reader:
            rows.append(row)
    
    # 정렬 함수: 숫자로 변환 가능하면 숫자로, 아니면 문자열로 비교
    def sort_key(row):
        value = row.get(sort_column, '').strip()
        if not value:
            # 빈 값은 맨 뒤로
            return (1, '')
        
        # 숫자로 변환 시도
        try:
            return (0, int(value))
        except ValueError:
            try:
                return (0, float(value))
            except ValueError:
                # 문자열로 비교
                return (0, value)
    
    # 정렬 수행
    sorted_rows = sorted(rows, key=sort_key, reverse=reverse)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  정렬 기준 컬럼: {sort_column}")
    print(f"  정렬 방향: {'내림차순' if reverse else '오름차순'}")
    print(f"  총 행 수: {len(sorted_rows)}개 (헤더 제외)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python script/sort_rows_custom.py <input_file> <sort_column> [--reverse] [output_file]")
        print("예시: python script/sort_rows_custom.py alll.csv VocabularyId")
        print("      python script/sort_rows_custom.py alll.csv VocabularyId --reverse")
        sys.exit(1)
    
    input_file = sys.argv[1]
    sort_column = sys.argv[2]
    
    # --reverse 옵션 확인
    reverse = '--reverse' in sys.argv
    
    # 출력 파일명 확인 (--reverse가 아닌 마지막 인자 중 .csv로 끝나는 것)
    output_file = None
    for arg in reversed(sys.argv[3:]):
        if arg != '--reverse' and arg.endswith('.csv'):
            output_file = arg
            break
    
    sort_rows_by_column(input_file, sort_column, output_file, reverse)

