#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vocabulary_join_Meaning.csv와 Meaning_join_Example.csv를 합치는 스크립트
사용법: python script/join/2_Vocabulary_Meaning_Example.py [join_type] [output_file]
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
    output_dir = os.path.join(data_dir, 'output')
    
    left_file = os.path.join(output_dir, 'Vocabulary_join_Meaning.csv')
    right_file = os.path.join(output_dir, 'Meaning_join_Example.csv')
    
    # 조인 키 설정: 두 파일 모두 MeaningId를 가지고 있음
    left_key = 'MeaningId'  # Vocabulary_join_Meaning.csv의 MeaningId
    right_key = 'MeaningId'  # Meaning_join_Example.csv의 MeaningId
    
    # 인자 파싱
    join_type = 'inner'
    output_file = None
    
    if len(sys.argv) > 1:
        join_type = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # 출력 파일이 지정되지 않으면 자동 생성
    if output_file is None:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'Vocabulary_Meaning_Example.csv')
    
    # 조인 수행
    join_csv_files(left_file, right_file, left_key, right_key, 
                   join_type=join_type, output_file=output_file)

if __name__ == "__main__":
    main()

