#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vocabulary.db의 테이블을 CSV 파일로 내보내는 스크립트 (name.py의 반대 기능)
CSV 파일명이 데이터베이스의 테이블명과 일치해야 합니다.
사용법: python script/export_db_to_csv.py <csv_file> <db_file>
"""

import csv
import sqlite3
import sys
import os

def get_table_name_from_csv(csv_file):
    """
    CSV 파일명에서 테이블명 추출 (확장자 제거)
    
    Args:
        csv_file: CSV 파일 경로
        
    Returns:
        테이블명
    """
    base_name = os.path.basename(csv_file)
    table_name = os.path.splitext(base_name)[0]
    return table_name

def get_table_schema(cursor, table_name):
    """
    테이블의 스키마 정보 가져오기
    
    Args:
        cursor: 데이터베이스 커서
        table_name: 테이블명
        
    Returns:
        컬럼 정보 리스트 [(index, name, type, notnull, default, pk), ...]
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def get_reverse_column_mapping(db_columns):
    """
    DB 컬럼명을 CSV 컬럼명에 매핑 (역매핑)
    특수 매핑 규칙: example_sentence -> Example
    
    Args:
        db_columns: DB 컬럼명 리스트
        
    Returns:
        딕셔너리 {db_column: csv_column}
    """
    mapping = {}
    
    # 특수 매핑 규칙 (역방향)
    special_mappings = {
        'example_sentence': 'Example',
    }
    
    for db_col in db_columns:
        # 특수 매핑 규칙
        if db_col in special_mappings:
            mapping[db_col] = special_mappings[db_col]
        else:
            # 그대로 사용
            mapping[db_col] = db_col
    
    return mapping

def export_table_to_csv(csv_file, db_file, force=False):
    """
    vocabulary.db의 테이블 데이터를 CSV 파일로 내보내기
    CSV 파일명이 테이블명과 일치해야 합니다.
    
    Args:
        csv_file: 출력 CSV 파일 경로
        db_file: SQLite 데이터베이스 파일 경로
        force: 기존 파일을 강제로 덮어쓸지 여부
    """
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 입력 파일의 디렉토리에 output 폴더 생성
    csv_dir = os.path.dirname(os.path.abspath(csv_file))
    output_dir = os.path.join(csv_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV 파일을 output 폴더에 저장
    csv_filename = os.path.basename(csv_file)
    csv_file = os.path.join(output_dir, csv_filename)
    
    # 기존 파일이 있고 force 옵션이 없으면 경고
    if os.path.exists(csv_file) and not force:
        print(f"경고: 파일 '{csv_file}'이 이미 존재합니다.")
        print("      덮어쓰려면 -rf 옵션을 사용하세요.")
        sys.exit(1)
    
    # CSV 파일명에서 테이블명 추출
    table_name = get_table_name_from_csv(csv_file)
    print(f"테이블명: {table_name}")
    
    # 데이터베이스 연결
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 테이블 존재 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        print(f"오류: 데이터베이스에 '{table_name}' 테이블이 존재하지 않습니다.")
        conn.close()
        sys.exit(1)
    
    # 테이블 스키마 가져오기
    schema = get_table_schema(cursor, table_name)
    db_columns = [col[1] for col in schema]  # 컬럼명만 추출
    print(f"데이터베이스 컬럼: {', '.join(db_columns)}")
    
    # 역매핑 생성 (DB 컬럼 -> CSV 컬럼)
    reverse_mapping = get_reverse_column_mapping(db_columns)
    csv_columns = [reverse_mapping.get(col, col) for col in db_columns]
    print(f"CSV 컬럼: {', '.join(csv_columns)}")
    
    # 데이터 가져오기
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY Id")
    rows = cursor.fetchall()
    
    conn.close()
    
    # CSV 파일로 저장
    with open(csv_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=csv_columns)
        writer.writeheader()
        
        for row in rows:
            # DB 컬럼 순서대로 딕셔너리 생성
            row_dict = {}
            for i, db_col in enumerate(db_columns):
                csv_col = reverse_mapping.get(db_col, db_col)
                value = row[i] if row[i] is not None else ''
                row_dict[csv_col] = value
            
            writer.writerow(row_dict)
    
    print(f"\n내보내기 완료!")
    print(f"  데이터베이스: {db_file}")
    print(f"  테이블: {table_name}")
    print(f"  출력 파일: {csv_file}")
    print(f"  총 행 수: {len(rows)}개 (헤더 제외)")

if __name__ == "__main__":
    # 인자 확인
    if len(sys.argv) < 3:
        print("사용법: python script/export_db_to_csv.py <csv_file> <db_file> [-rf]")
        print("예시: python script/export_db_to_csv.py Example.csv vocabulary.db")
        print("      python script/export_db_to_csv.py Example.csv vocabulary.db -rf")
        print("      (name.py의 반대 기능: DB -> CSV)")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    db_file = sys.argv[2]
    force = '-rf' in sys.argv
    
    export_table_to_csv(csv_file, db_file, force)

