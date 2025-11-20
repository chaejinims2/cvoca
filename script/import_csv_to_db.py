#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일을 vocabulary.db에 중복을 제외하고 업데이트하는 스크립트
CSV 파일명이 데이터베이스의 테이블명과 일치해야 합니다.
사용법: ./script/import_csv_to_db.py Vocabulary.csv vocabulary.db [-rf]
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

def get_column_mapping(csv_columns, db_columns):
    """
    CSV 컬럼명을 DB 컬럼명에 매핑
    우선순위: 1) 정확히 일치, 2) 대소문자 무시 일치, 3) 특수 매핑 규칙
    
    Args:
        csv_columns: CSV 컬럼명 리스트
        db_columns: DB 컬럼명 리스트
        
    Returns:
        딕셔너리 {csv_column: db_column}
    """
    mapping = {}
    db_columns_lower = {col.lower(): col for col in db_columns}
    
    # 특수 매핑 규칙
    special_mappings = {
        'Example': 'example_sentence',
        'example': 'example_sentence',
    }
    
    for csv_col in csv_columns:
        # 1. 정확히 일치
        if csv_col in db_columns:
            mapping[csv_col] = csv_col
        # 2. 특수 매핑 규칙
        elif csv_col in special_mappings:
            if special_mappings[csv_col] in db_columns:
                mapping[csv_col] = special_mappings[csv_col]
        # 3. 대소문자 무시 일치
        elif csv_col.lower() in db_columns_lower:
            mapping[csv_col] = db_columns_lower[csv_col.lower()]
        # 매핑 실패
        else:
            print(f"경고: CSV 컬럼 '{csv_col}'에 해당하는 DB 컬럼을 찾을 수 없습니다.")
    
    return mapping

def update_table_from_csv(csv_file, db_file, force=False):
    """
    CSV 파일의 데이터를 vocabulary.db의 해당 테이블에 업데이트
    CSV 파일명이 테이블명과 일치해야 합니다.
    
    Args:
        csv_file: CSV 파일 경로
        db_file: SQLite 데이터베이스 파일 경로
        force: 중복 시 덮어쓸지 여부 (True면 UPDATE, False면 건너뛰기)
    """
    # 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"오류: CSV 파일 '{csv_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
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
    
    # Primary Key 컬럼 찾기
    primary_key = None
    pk_columns = [col[1] for col in schema if col[5]]  # col[5]는 pk 플래그
    
    if pk_columns:
        primary_key = pk_columns[0]
    else:
        # Primary Key가 없으면 규칙에 따라 찾기
        # 규칙: 테이블명에서 끝의 's'를 제거하고 'Id'를 추가
        # 예: Words -> word_id, Examples -> example_id, Definitions -> definition_id
        if table_name.endswith('s'):
            singular_name = table_name[:-1]  # 끝의 's' 제거
            expected_pk = f"{singular_name}Id"
        else:
            expected_pk = f"{table_name}Id"
        
        # 예상된 Primary Key 컬럼이 존재하는지 확인
        if expected_pk in db_columns:
            primary_key = expected_pk
        else:
            # 없으면 Id로 끝나는 컬럼 중 가장 짧은 것 선택
            id_columns = [col[1] for col in schema if col[1].endswith('Id')]
            if id_columns:
                primary_key = min(id_columns, key=len)
            elif 'Id' in db_columns:
                primary_key = 'Id'
    
    if not primary_key:
        print(f"오류: '{table_name}' 테이블에서 Primary Key 또는 Id 컬럼을 찾을 수 없습니다.")
        conn.close()
        sys.exit(1)
    
    print(f"Primary Key 컬럼: {primary_key}")
    
    # 기존 데이터의 Primary Key 목록 가져오기 (중복 체크용)
    cursor.execute(f"SELECT {primary_key} FROM {table_name}")
    existing_ids = set(row[0] for row in cursor.fetchall())
    
    # CSV 파일 읽기
    new_rows = []
    skipped_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        csv_columns = reader.fieldnames
        
        print(f"CSV 컬럼: {', '.join(csv_columns)}")
        
        # Primary Key 컬럼이 CSV에 있는지 확인
        csv_pk = None
        if primary_key in csv_columns:
            csv_pk = primary_key
        else:
            # 매핑된 컬럼에서 찾기
            column_mapping = get_column_mapping(csv_columns, db_columns)
            reverse_mapping = {db_col: csv_col for csv_col, db_col in column_mapping.items()}
            if primary_key in reverse_mapping:
                csv_pk = reverse_mapping[primary_key]
        
        if not csv_pk:
            print(f"오류: CSV 파일에 Primary Key 컬럼 '{primary_key}'에 해당하는 컬럼이 없습니다.")
            print(f"      CSV 컬럼: {', '.join(csv_columns)}")
            conn.close()
            sys.exit(1)
        
        # CSV 컬럼과 DB 컬럼 매핑
        column_mapping = get_column_mapping(csv_columns, db_columns)
        
        # 매핑된 컬럼만 사용
        columns_to_insert = [col for col in db_columns if col in column_mapping.values()]
        placeholders = ','.join(['?' for _ in columns_to_insert])
        columns_str = ','.join(columns_to_insert)
        
        # 역매핑 생성 (DB 컬럼 -> CSV 컬럼)
        reverse_mapping = {db_col: csv_col for csv_col, db_col in column_mapping.items()}
        
        # CSV에 없는 DB 컬럼 확인
        missing_columns = set(db_columns) - set(columns_to_insert)
        if missing_columns:
            print(f"경고: CSV에 없는 DB 컬럼: {', '.join(missing_columns)}")
            print("      이 컬럼들은 NULL 또는 기본값으로 설정됩니다.")
        
        for row in reader:
            # Primary Key가 비어있으면 건너뛰기
            if not row.get(csv_pk, '').strip():
                continue
            
            try:
                row_id = int(row[csv_pk].strip())
                
                # CSV 행에서 DB 컬럼에 해당하는 값만 추출
                values = []
                for db_col in columns_to_insert:
                    # DB 컬럼에 매핑된 CSV 컬럼명 찾기
                    csv_col = reverse_mapping.get(db_col, db_col)
                    value = row.get(csv_col, '').strip()
                    # 빈 문자열은 None으로 변환
                    if value == '':
                        values.append(None)
                    else:
                        values.append(value)
                
                # 중복 체크: Primary Key가 이미 존재하는지 확인
                if row_id in existing_ids:
                    if force:
                        # 덮어쓰기: UPDATE 쿼리 실행
                        update_values = values + [row_id]  # 마지막에 Primary Key 추가
                        update_set = ', '.join([f"{col} = ?" for col in columns_to_insert])
                        update_query = f"UPDATE {table_name} SET {update_set} WHERE {primary_key} = ?"
                        cursor.execute(update_query, update_values)
                        skipped_count += 1  # 업데이트된 항목으로 카운트
                    else:
                        # 건너뛰기
                        skipped_count += 1
                        continue
                else:
                    # 새 데이터 추가
                    new_rows.append(tuple(values))
                    existing_ids.add(row_id)  # 메모리에서도 중복 방지
                
            except ValueError as e:
                print(f"경고: 행을 건너뜁니다 - Primary Key가 숫자가 아닙니다: {row.get(csv_pk, 'N/A')}")
                continue
    
    # 새 데이터 삽입
    if new_rows:
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        cursor.executemany(insert_query, new_rows)
        print(f"성공: {len(new_rows)}개의 새 항목이 추가되었습니다.")
    
    # 변경사항 커밋
    conn.commit()
    
    if skipped_count > 0:
        if force:
            print(f"업데이트된 중복 항목: {skipped_count}개")
        else:
            print(f"건너뛴 중복 항목: {skipped_count}개")
    
    if not new_rows and not skipped_count:
        print("처리할 항목이 없습니다.")
    
    # 최종 통계
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_count = cursor.fetchone()[0]
    print(f"'{table_name}' 테이블의 총 항목 수: {total_count}개")
    
    conn.close()

if __name__ == "__main__":
    # 인자 확인
    if len(sys.argv) < 3:
        print("사용법: python script/import_csv_to_db.py <csv_file> <db_file> [-rf]")
        print("예시: python script/import_csv_to_db.py Vocabulary.csv vocabulary.db")
        print("      python script/import_csv_to_db.py Vocabulary.csv vocabulary.db -rf")
        print("      (-rf 옵션: 중복 시 기존 데이터를 덮어씁니다)")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    db_file = sys.argv[2]
    force = '-rf' in sys.argv
    
    update_table_from_csv(csv_file, db_file, force)

