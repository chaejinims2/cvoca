#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터베이스의 모든 테이블을 각각 CSV 파일로 내보내는 스크립트
각 테이블은 테이블명.csv 파일로 저장됩니다.

사용법: python script/export_all_tables_to_csv.py <db_file> [output_dir] [--overwrite]
예시: python script/export_all_tables_to_csv.py vocabulary.db
      python script/export_all_tables_to_csv.py vocabulary.db data/output
      python script/export_all_tables_to_csv.py vocabulary.db data/output --overwrite
"""

import csv
import sqlite3
import sys
import os


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


def export_table_to_csv(cursor, table_name, output_file, force=False):
    """
    단일 테이블을 CSV 파일로 내보내기
    
    Args:
        cursor: 데이터베이스 커서
        table_name: 테이블명
        output_file: 출력 CSV 파일 경로
        force: 기존 파일을 강제로 덮어쓸지 여부
        
    Returns:
        내보낸 행 수
    """
    # 기존 파일이 있고 force 옵션이 없으면 경고
    if os.path.exists(output_file) and not force:
        print(f"  경고: 파일 '{output_file}'이 이미 존재합니다. 건너뜁니다.")
        return 0
    
    # 테이블 스키마 가져오기
    schema = get_table_schema(cursor, table_name)
    db_columns = [col[1] for col in schema]  # 컬럼명만 추출
    
    # 역매핑 생성 (DB 컬럼 -> CSV 컬럼)
    reverse_mapping = get_reverse_column_mapping(db_columns)
    csv_columns = [reverse_mapping.get(col, col) for col in db_columns]
    
    # 데이터 가져오기
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # CSV 파일로 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
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
    
    return len(rows)


def export_all_tables_to_csv(db_file, output_dir=None, force=False):
    """
    데이터베이스의 모든 테이블을 각각 CSV 파일로 내보내기
    
    Args:
        db_file: SQLite 데이터베이스 파일 경로
        output_dir: 출력 디렉토리 (None이면 DB 파일과 같은 디렉토리)
        force: 기존 파일을 강제로 덮어쓸지 여부
    """
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 출력 디렉토리 설정
    if output_dir is None:
        # DB 파일과 같은 디렉토리
        db_dir = os.path.dirname(os.path.abspath(db_file))
        output_dir = os.path.join(db_dir, 'output')
    else:
        output_dir = os.path.abspath(output_dir)
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 데이터베이스 연결
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 모든 테이블 목록 가져오기
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    if not tables:
        print(f"경고: 데이터베이스 '{db_file}'에 테이블이 없습니다.")
        conn.close()
        return
    
    print(f"데이터베이스: {db_file}")
    print(f"출력 디렉토리: {output_dir}")
    print(f"테이블 수: {len(tables)}개\n")
    
    total_rows = 0
    exported_tables = []
    
    # 각 테이블을 CSV로 내보내기
    for (table_name,) in tables:
        csv_filename = f"{table_name}.csv"
        csv_file = os.path.join(output_dir, csv_filename)
        
        print(f"처리 중: {table_name} -> {csv_filename}")
        
        try:
            row_count = export_table_to_csv(cursor, table_name, csv_file, force)
            total_rows += row_count
            exported_tables.append((table_name, csv_filename, row_count))
            print(f"  완료: {row_count}개 행 내보냄")
        except Exception as e:
            print(f"  오류: {e}")
    
    conn.close()
    
    # 최종 통계
    print(f"\n=== 내보내기 완료 ===")
    print(f"데이터베이스: {db_file}")
    print(f"출력 디렉토리: {output_dir}")
    print(f"내보낸 테이블 수: {len(exported_tables)}개")
    print(f"총 내보낸 행 수: {total_rows}개\n")
    
    print("내보낸 파일:")
    for table_name, csv_filename, row_count in exported_tables:
        csv_path = os.path.join(output_dir, csv_filename)
        print(f"  {csv_filename} ({row_count}개 행) -> {csv_path}")


def main():
    if len(sys.argv) < 2:
        print("사용법: python script/export_all_tables_to_csv.py <db_file> [output_dir] [--overwrite]")
        print("예시: python script/export_all_tables_to_csv.py vocabulary.db")
        print("      python script/export_all_tables_to_csv.py vocabulary.db data/output")
        print("      python script/export_all_tables_to_csv.py vocabulary.db data/output --overwrite")
        print("\n옵션:")
        print("  output_dir: 출력 디렉토리 (기본값: DB 파일과 같은 디렉토리의 output 폴더)")
        print("  --overwrite: 기존 CSV 파일을 덮어씁니다")
        sys.exit(1)
    
    db_file = sys.argv[1]
    output_dir = None
    force = False
    
    # 인자 파싱
    for arg in sys.argv[2:]:
        if arg == '--overwrite':
            force = True
        elif not arg.startswith('--'):
            output_dir = arg
    
    export_all_tables_to_csv(db_file, output_dir, force)


if __name__ == "__main__":
    main()

