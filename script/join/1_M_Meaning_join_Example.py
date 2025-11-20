#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meaning.csv와 Example.csv를 조인하는 스크립트
단일 조인만 수행하며, 컬럼명은 변경하지 않음
사용법: python script/join/1_M_Meaning_join_Example.py [join_type] [output_file]
"""

import csv
import sys
import os

# 상위 디렉토리의 join_csv.py import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from join_csv import join_csv_files

def main():
    # 기본 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'data')
    
    left_file = os.path.join(data_dir, 'Meaning.csv')
    right_file = os.path.join(data_dir, 'Example.csv')
    
    # 조인 키 설정
    left_key = 'Id'  # Meaning.Id
    right_key = 'MeaningId'  # Example.MeaningId
    
    # 인자 파싱
    join_type = 'inner'
    output_file = None
    
    if len(sys.argv) > 1:
        join_type = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # 출력 파일이 지정되지 않으면 자동 생성
    if output_file is None:
        output_dir = os.path.join(data_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'Meaning_join_Example.csv')
    
    # 조인 수행
    join_csv_files(left_file, right_file, left_key, right_key, 
                   join_type=join_type, output_file=output_file)

if __name__ == "__main__":
    main()

