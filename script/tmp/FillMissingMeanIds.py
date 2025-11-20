#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example.csv에서 Meaning.csv의 모든 MeanId와 1:1 매핑되는지 확인하고
누락된 MeanId에 대해 example_no=0, Usage="TempWord_{ExamId}" 추가
사용법: python script/tmp/FillMissingMeanIds.py <example_file> <meaning_file> [output_file]
"""

import csv
import sys
import os

def fill_missing_mean_ids(example_file, meaning_file, output_file=None):
    """
    Example.csv에서 Meaning.csv의 모든 MeanId와 1:1 매핑되는지 확인하고 누락된 항목 추가
    
    Args:
        example_file: Example.csv 파일 경로
        meaning_file: Meaning.csv 파일 경로
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일 덮어쓰기)
    """
    # 파일 존재 확인
    for file_path in [example_file, meaning_file]:
        if not os.path.exists(file_path):
            print(f"오류: CSV 파일 '{file_path}'을 찾을 수 없습니다.")
            sys.exit(1)
    
    if output_file is None:
        output_file = example_file
    
    # Meaning.csv에서 모든 sense_no 읽기
    meaning_mean_ids = set()
    meaning_data = {}
    
    with open(meaning_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mean_id = row.get('sense_no', '').strip()
            if mean_id:
                try:
                    mean_id_int = int(mean_id)
                    meaning_mean_ids.add(mean_id_int)
                    meaning_data[mean_id_int] = row
                except ValueError:
                    pass
    
    print(f"Meaning.csv의 sense_no 개수: {len(meaning_mean_ids)}")
    
    # Example.csv에서 기존 sense_no 읽기
    existing_mean_ids = set()
    rows = []
    fieldnames = None
    
    with open(example_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None:
            print("오류: CSV 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        for row in reader:
            mean_id = row.get('sense_no', '').strip()
            if mean_id:
                try:
                    mean_id_int = int(mean_id)
                    existing_mean_ids.add(mean_id_int)
                except ValueError:
                    pass
            rows.append(row)
    
    print(f"Example.csv의 기존 sense_no 개수: {len(existing_mean_ids)}")
    
    # Meaning에 있지만 Example에 없는 sense_no 찾기
    missing_mean_ids = sorted(meaning_mean_ids - existing_mean_ids)
    
    print(f"누락된 sense_no 개수: {len(missing_mean_ids)}")
    
    if not missing_mean_ids:
        print("모든 MeanId가 이미 존재합니다. 추가할 항목이 없습니다.")
        return
    
    # 누락된 MeanId에 대해 새 행 추가
    new_rows = []
    for mean_id in missing_mean_ids:
        # example_no = 0
        use_id = 0
        # ExamId = sense_no * 10 + example_no
        exam_id = mean_id * 10 + use_id
        # Usage = "TempWord_{ExamId}"
        usage = f"TempWord_{exam_id}"
        
        new_row = {
            'sense_no': str(mean_id),
            'example_no': str(use_id),
            'ExamId': str(exam_id),
            'Usage': usage
        }
        new_rows.append(new_row)
        rows.append(new_row)
    
    # MeanId로 정렬 (숫자로 변환하여 정렬)
    def sort_key(row):
        try:
            return int(row.get('sense_no', '0'))
        except ValueError:
            return 0
    
    rows.sort(key=sort_key)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n처리 완료!")
    print(f"  입력 파일: {example_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  추가된 행: {len(new_rows)}개")
    if new_rows:
        print(f"  예시 (처음 5개):")
        for row in new_rows[:5]:
            print(f"    sense_no={row['sense_no']}, example_no={row['example_no']}, ExamId={row['ExamId']}, Usage={row['Usage']}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python script/tmp/FillMissingMeanIds.py <example_file> <meaning_file> [output_file]")
        print("예시: python script/tmp/FillMissingMeanIds.py data/Example.csv data/Meaning.csv")
        sys.exit(1)
    
    example_file = sys.argv[1]
    meaning_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    fill_missing_mean_ids(example_file, meaning_file, output_file)

