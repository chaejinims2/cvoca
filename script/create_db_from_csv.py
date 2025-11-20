#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일들로부터 새로운 SQLite 데이터베이스를 생성하는 스크립트
각 CSV 파일은 하나의 테이블이 됩니다.
CSV 파일명이 테이블명이 됩니다 (확장자 제외).

사용법: python script/create_db_from_csv.py <output_db> <csv_file1> [csv_file2] [csv_file3] ...
예시: python script/create_db_from_csv.py vocabulary.db Vocabulary.csv Meaning.csv Example.csv
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


def infer_column_type(column_name, sample_values):
    """
    컬럼명과 샘플 값들을 기반으로 데이터 타입 추론
    
    Args:
        column_name: 컬럼명
        sample_values: 샘플 값 리스트
        
    Returns:
        SQLite 데이터 타입 (INTEGER, TEXT, REAL 등)
    """
    # Id로 끝나는 컬럼은 INTEGER로 추정
    if column_name.lower().endswith('id'):
        return 'INTEGER'
    
    # 샘플 값들 확인
    integer_count = 0
    real_count = 0
    
    for value in sample_values:
        if value is None or value.strip() == '':
            continue
        try:
            int(value.strip())
            integer_count += 1
        except ValueError:
            try:
                float(value.strip())
                real_count += 1
            except ValueError:
                pass
    
    # 모든 값이 정수면 INTEGER
    if integer_count > 0 and integer_count == len([v for v in sample_values if v and v.strip()]):
        return 'INTEGER'
    
    # 일부가 실수면 REAL
    if real_count > 0:
        return 'REAL'
    
    # 기본값은 TEXT
    return 'TEXT'


def create_table_from_csv(cursor, csv_file, table_name):
    """
    CSV 파일을 읽어서 테이블을 생성하고 데이터를 삽입
    
    Args:
        cursor: 데이터베이스 커서
        csv_file: CSV 파일 경로
        table_name: 생성할 테이블명
        
    Returns:
        삽입된 행 수
    """
    if not os.path.exists(csv_file):
        print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
        return 0
    
    print(f"\n처리 중: {table_name} 테이블 ({csv_file})")
    
    # CSV 파일 읽기
    with open(csv_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        csv_columns = reader.fieldnames
        
        if not csv_columns:
            print(f"경고: '{csv_file}' 파일에 컬럼이 없습니다. 건너뜁니다.")
            return 0
        
        print(f"  컬럼: {', '.join(csv_columns)}")
        
        # 데이터 타입 추론을 위해 첫 몇 행 읽기
        rows_for_inference = []
        for i, row in enumerate(reader):
            rows_for_inference.append(row)
            if i >= 10:  # 최대 10행만 샘플로 사용
                break
        
        # 각 컬럼의 데이터 타입 추론
        column_types = {}
        for col in csv_columns:
            sample_values = [row.get(col, '') for row in rows_for_inference]
            column_types[col] = infer_column_type(col, sample_values)
        
        # Primary Key 자동 감지
        # 규칙: 파일명(테이블명)에서 끝의 's'를 제거하고 'Id'를 추가
        # 예: Words -> word_id, Examples -> example_id, Definitions -> definition_id
        primary_key = None
        
        # 테이블명에서 끝의 's' 제거 후 'Id' 추가
        if table_name.endswith('s'):
            singular_name = table_name[:-1]  # 끝의 's' 제거
            expected_pk = f"{singular_name}Id"
        else:
            expected_pk = f"{table_name}Id"
        
        # 예상된 Primary Key 컬럼이 존재하는지 확인
        if expected_pk in csv_columns:
            primary_key = expected_pk
        else:
            # 없으면 Id로 끝나는 컬럼 중 가장 짧은 것 선택
            id_columns = [col for col in csv_columns if col.endswith('Id')]
            if id_columns:
                primary_key = min(id_columns, key=len)
        
        # CREATE TABLE SQL 생성
        column_defs = []
        for col in csv_columns:
            col_def = f'"{col}" {column_types[col]}'
            if col == primary_key:
                col_def += " PRIMARY KEY"
            column_defs.append(col_def)
        
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        
        # 테이블 생성
        cursor.execute(create_table_sql)
        if primary_key:
            print(f"  테이블 생성 완료 (Primary Key: {primary_key})")
        else:
            print(f"  테이블 생성 완료 (Primary Key 없음)")
        
        # 데이터 삽입 준비
        placeholders = ','.join(['?' for _ in csv_columns])
        columns_str = ','.join([f'"{col}"' for col in csv_columns])
        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # 첫 행부터 다시 읽기 (이미 읽은 행들 포함)
        infile.seek(0)
        reader = csv.DictReader(infile)
        
        # 데이터 삽입
        rows_to_insert = []
        for row in reader:
            values = []
            for col in csv_columns:
                value = row.get(col, '').strip()
                # 빈 문자열은 None으로 변환
                if value == '':
                    values.append(None)
                else:
                    # 타입에 맞게 변환
                    col_type = column_types[col]
                    if col_type == 'INTEGER':
                        try:
                            values.append(int(value) if value else None)
                        except ValueError:
                            values.append(None)
                    elif col_type == 'REAL':
                        try:
                            values.append(float(value) if value else None)
                        except ValueError:
                            values.append(None)
                    else:
                        values.append(value)
            rows_to_insert.append(tuple(values))
        
        # 배치 삽입
        cursor.executemany(insert_sql, rows_to_insert)
        inserted_count = len(rows_to_insert)
        print(f"  데이터 삽입 완료: {inserted_count}개 행")
        
        return inserted_count


def create_database_from_csvs(output_db, csv_files, overwrite=False):
    """
    여러 CSV 파일로부터 새로운 데이터베이스 생성
    
    Args:
        output_db: 출력 데이터베이스 파일 경로
        csv_files: CSV 파일 경로 리스트
        overwrite: 기존 DB 파일을 덮어쓸지 여부
    """
    # 출력 파일이 이미 존재하는지 확인
    if os.path.exists(output_db) and not overwrite:
        print(f"오류: 데이터베이스 파일 '{output_db}'이 이미 존재합니다.")
        print("      덮어쓰려면 --overwrite 옵션을 사용하세요.")
        sys.exit(1)
    
    # CSV 파일 존재 확인
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
            sys.exit(1)
    
    # 기존 파일 삭제 (overwrite 옵션이 있으면)
    if os.path.exists(output_db) and overwrite:
        os.remove(output_db)
        print(f"기존 데이터베이스 파일 '{output_db}' 삭제됨")
    
    # 데이터베이스 연결
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()
    
    print(f"새 데이터베이스 생성: {output_db}")
    print(f"CSV 파일 수: {len(csv_files)}")
    
    total_tables = 0
    total_rows = 0
    
    # 각 CSV 파일을 테이블로 변환
    for csv_file in csv_files:
        table_name = get_table_name_from_csv(csv_file)
        row_count = create_table_from_csv(cursor, csv_file, table_name)
        total_tables += 1
        total_rows += row_count
    
    # 변경사항 커밋
    conn.commit()
    
    # 최종 통계
    print(f"\n=== 생성 완료 ===")
    print(f"데이터베이스 파일: {output_db}")
    print(f"생성된 테이블 수: {total_tables}")
    print(f"총 삽입된 행 수: {total_rows}")
    
    # 각 테이블의 행 수 출력
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n테이블별 행 수:")
    for (table_name,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count}개 행")
    
    conn.close()


def main():
    if len(sys.argv) < 3:
        print("사용법: python script/create_db_from_csv.py <output_db> <csv_file1> [csv_file2] [csv_file3] ...")
        print("예시: python script/create_db_from_csv.py vocabulary.db Vocabulary.csv Meaning.csv Example.csv")
        print("      python script/create_db_from_csv.py vocabulary.db *.csv --overwrite")
        print("\n옵션:")
        print("  --overwrite: 기존 데이터베이스 파일을 덮어씁니다")
        sys.exit(1)
    
    # 인자 파싱
    args = sys.argv[1:]
    overwrite = '--overwrite' in args
    if overwrite:
        args.remove('--overwrite')
    
    output_db = args[0]
    csv_files = args[1:]
    
    if not csv_files:
        print("오류: 최소 하나의 CSV 파일을 지정해야 합니다.")
        sys.exit(1)
    
    create_database_from_csvs(output_db, csv_files, overwrite)


if __name__ == "__main__":
    main()

