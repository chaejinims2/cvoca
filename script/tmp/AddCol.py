#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일에 값이 없어도 되는 int형 컬럼을 추가하는 스크립트
사용법: python script/tmp/AddCol.py <csv_file> <column_name> [position] [default_value]
예시: python script/tmp/AddCol.py data/Meaning.csv NewColumn
     python script/tmp/AddCol.py data/Meaning.csv NewColumn end
     python script/tmp/AddCol.py data/Meaning.csv NewColumn after VocabularyId
     python script/tmp/AddCol.py data/Meaning.csv NewColumn end 0
"""

import csv
import sys
import os

def add_column(csv_file, column_name, position='end', default_value=None, force=False):
    """
    CSV 파일에 int형 컬럼 추가 (값이 없어도 됨)
    
    Args:
        csv_file: CSV 파일 경로
        column_name: 추가할 컬럼명
        position: 컬럼 위치 ('end', 'start', 또는 'after <column_name>')
        default_value: 기본값 (None이면 빈 문자열)
        force: 컬럼이 이미 존재할 때 덮어쓸지 여부
    """
    # 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # CSV 파일 읽기
    rows = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        if fieldnames is None:
            print("오류: CSV 파일에 헤더가 없습니다.")
            sys.exit(1)
        
        # 컬럼이 이미 있는지 확인
        if column_name in fieldnames:
            if force:
                print(f"경고: '{column_name}' 컬럼이 이미 존재합니다. 기존 값을 덮어씁니다.")
            else:
                print(f"오류: '{column_name}' 컬럼이 이미 존재합니다.")
                print("      덮어쓰려면 -rf 옵션을 사용하세요.")
                sys.exit(1)
        else:
            # 컬럼 위치 결정
            if position == 'end':
                fieldnames.append(column_name)
            elif position == 'start':
                fieldnames.insert(0, column_name)
            elif position.startswith('after '):
                after_column = position.replace('after ', '').strip()
                if after_column not in fieldnames:
                    print(f"오류: '{after_column}' 컬럼이 파일에 존재하지 않습니다.")
                    print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
                    sys.exit(1)
                after_index = fieldnames.index(after_column)
                fieldnames.insert(after_index + 1, column_name)
            else:
                print(f"경고: 알 수 없는 위치 '{position}'. 'end'로 설정합니다.")
                fieldnames.append(column_name)
        
        # 기본값 설정
        if default_value is not None:
            try:
                # int형으로 변환 가능한지 확인
                int(default_value)
                default_str = str(default_value)
            except ValueError:
                print(f"경고: 기본값 '{default_value}'를 int로 변환할 수 없습니다. 빈 값으로 설정합니다.")
                default_str = ''
        else:
            default_str = ''
        
        for row in reader:
            # 새 컬럼에 기본값 또는 빈 값 설정
            row[column_name] = default_str
            rows.append(row)
    
    # CSV 파일에 쓰기
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  파일: {csv_file}")
    print(f"  추가된 컬럼: {column_name}")
    print(f"  위치: {position}")
    if default_value is not None:
        print(f"  기본값: {default_value}")
    else:
        print(f"  기본값: (빈 값)")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")

def main():
    if len(sys.argv) < 3:
        print("사용법: python script/tmp/AddCol.py <csv_file> <column_name> [position] [default_value] [-rf]")
        print("예시: python script/tmp/AddCol.py data/Meaning.csv NewColumn")
        print("      python script/tmp/AddCol.py data/Meaning.csv NewColumn end")
        print("      python script/tmp/AddCol.py data/Meaning.csv NewColumn after VocabularyId")
        print("      python script/tmp/AddCol.py data/Meaning.csv NewColumn end 0")
        print("      python script/tmp/AddCol.py data/Meaning.csv NewColumn end 0 -rf")
        print("\n위치 옵션:")
        print("  end: 마지막에 추가 (기본값)")
        print("  start: 맨 앞에 추가")
        print("  after <column_name>: 지정한 컬럼 다음에 추가")
        print("\n기본값: 지정하지 않으면 빈 값('')으로 설정")
        print("-rf: 컬럼이 이미 존재할 때 덮어쓰기")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    column_name = sys.argv[2]
    
    # 옵션 파싱
    force = '-rf' in sys.argv
    args_without_rf = [arg for arg in sys.argv[3:] if arg != '-rf']
    
    position = 'end'
    default_value = None
    
    if len(args_without_rf) > 0:
        # 첫 번째 인자가 위치인지 기본값인지 확인
        first_arg = args_without_rf[0]
        if first_arg in ['end', 'start'] or first_arg.startswith('after '):
            position = first_arg
            # 두 번째 인자가 있으면 기본값
            if len(args_without_rf) > 1:
                try:
                    default_value = int(args_without_rf[1])
                except ValueError:
                    print(f"경고: 기본값 '{args_without_rf[1]}'를 int로 변환할 수 없습니다. 빈 값으로 설정합니다.")
        else:
            # 첫 번째 인자가 숫자면 기본값
            try:
                default_value = int(first_arg)
            except ValueError:
                print(f"경고: '{first_arg}'를 위치 또는 기본값으로 인식할 수 없습니다. 'end' 위치로 설정합니다.")
    
    add_column(csv_file, column_name, position, default_value, force)

if __name__ == "__main__":
    main()

