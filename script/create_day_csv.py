#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
day_no를 입력받아 기본 CSV 파일을 생성하는 스크립트

사용법:
    python script/create_day_csv.py <day_no> [output_dir] [words_csv]

예시:
    python script/create_day_csv.py 14 data/ielts_voca_20_30/user/words data/words.csv
"""

import csv
import sys
import os


def create_day_csv(day_no, output_dir='data/words', words_csv='data/Words.csv'):
    """
    day_no에 해당하는 기본 CSV 파일 생성
    
    Args:
        day_no: day 번호
        output_dir: 출력 디렉토리
        words_csv: Words.csv 파일 경로
    """
    # 파일 존재 확인
    if not os.path.exists(words_csv):
        print(f"오류: 파일 '{words_csv}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # day_no 확인
    try:
        day_no_int = int(day_no)
    except ValueError:
        print(f"오류: day_no는 숫자여야 합니다: {day_no}")
        sys.exit(1)
    
    # Words.csv에서 day_no에 해당하는 word_id 찾기
    word_ids = []
    with open(words_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # 필수 컬럼 확인
        if 'day_no' not in reader.fieldnames:
            print(f"오류: '{words_csv}' 파일에 'day_no' 컬럼이 없습니다.")
            sys.exit(1)
        
        if 'word_id' not in reader.fieldnames:
            print(f"오류: '{words_csv}' 파일에 'word_id' 컬럼이 없습니다.")
            sys.exit(1)
        
        for row in reader:
            try:
                row_day_no = int(row['day_no'])
                if row_day_no == day_no_int:
                    word_id = int(row['word_id'])
                    word_ids.append(word_id)
            except ValueError:
                continue
    
    if not word_ids:
        print(f"경고: day_no={day_no_int}인 행을 찾을 수 없습니다.")
        sys.exit(1)
    
    # word_id 정렬
    word_ids.sort()
    
    print(f"day_no={day_no_int}에 해당하는 word_id: {len(word_ids)}개")
    print(f"  범위: {min(word_ids)} ~ {max(word_ids)}")
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV 파일 생성
    output_file = os.path.join(output_dir, f"{day_no}.csv")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['word_id', 'word'])  # 헤더
        
        for word_id in word_ids:
            writer.writerow([word_id, ''])  # word는 빈 값
    
    print(f"\n=== CSV 파일 생성 완료 ===")
    print(f"파일: {output_file}")
    print(f"행 수: {len(word_ids)}개 (헤더 제외)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법: python script/create_day_csv.py <day_no> [output_dir] [words_csv]")
        print("\n예시:")
        print("  python script/create_day_csv.py 14")
        print("  python script/create_day_csv.py 14 data/words")
        print("  python script/create_day_csv.py 14 data/words data/Words.csv")
        sys.exit(1)
    
    day_no = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'data/words'
    words_csv = sys.argv[3] if len(sys.argv) > 3 else 'data/Words.csv'
    
    create_day_csv(day_no, output_dir, words_csv)

