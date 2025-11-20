#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLite 데이터베이스의 테이블명과 컬럼명을 변경하는 스크립트

사용법:
1. 테이블명 변경:
   python script/rename_table_column.py data/vocabulary.db --rename-table old_name new_name

2. 컬럼명 변경:
   python script/rename_table_column.py data/vocabulary.db --rename-column table_name old_column new_column

3. 여러 컬럼명 변경:
   python script/rename_table_column.py data/vocabulary.db --rename-column table_name old1 new1 --rename-column table_name old2 new2
"""

import sqlite3
import sys
import os
import argparse


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


def get_create_table_sql(cursor, table_name):
    """
    테이블의 CREATE TABLE SQL 문 가져오기
    
    Args:
        cursor: 데이터베이스 커서
        table_name: 테이블명
        
    Returns:
        CREATE TABLE SQL 문
    """
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    result = cursor.fetchone()
    return result[0] if result else None


def rename_table(db_file, old_name, new_name):
    """
    테이블명 변경
    
    Args:
        db_file: 데이터베이스 파일 경로
        old_name: 기존 테이블명
        new_name: 새 테이블명
    """
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 테이블 존재 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_name,))
    if not cursor.fetchone():
        print(f"오류: 테이블 '{old_name}'이 존재하지 않습니다.")
        conn.close()
        sys.exit(1)
    
    # 새 테이블명이 이미 존재하는지 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (new_name,))
    if cursor.fetchone():
        print(f"오류: 테이블 '{new_name}'이 이미 존재합니다.")
        conn.close()
        sys.exit(1)
    
    try:
        # 테이블명 변경
        cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
        conn.commit()
        print(f"✓ 테이블명 변경 완료: '{old_name}' -> '{new_name}'")
    except sqlite3.Error as e:
        print(f"오류: 테이블명 변경 실패 - {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def rename_column(db_file, table_name, old_column, new_column):
    """
    컬럼명 변경 (SQLite는 직접 지원하지 않으므로 테이블 재생성 필요)
    
    Args:
        db_file: 데이터베이스 파일 경로
        table_name: 테이블명
        old_column: 기존 컬럼명
        new_column: 새 컬럼명
    """
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 테이블 존재 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        print(f"오류: 테이블 '{table_name}'이 존재하지 않습니다.")
        conn.close()
        sys.exit(1)
    
    # 기존 컬럼 확인
    schema = get_table_schema(cursor, table_name)
    column_names = [col[1] for col in schema]
    
    if old_column not in column_names:
        print(f"오류: 컬럼 '{old_column}'이 테이블 '{table_name}'에 존재하지 않습니다.")
        print(f"      사용 가능한 컬럼: {', '.join(column_names)}")
        conn.close()
        sys.exit(1)
    
    if new_column in column_names:
        print(f"오류: 컬럼 '{new_column}'이 이미 테이블 '{table_name}'에 존재합니다.")
        conn.close()
        sys.exit(1)
    
    try:
        # 1. 새 컬럼명으로 변경된 스키마 생성
        new_schema = []
        for col in schema:
            col_name = col[1]
            if col_name == old_column:
                col_name = new_column
            new_schema.append((col[0], col_name, col[2], col[3], col[4], col[5]))
        
        # 2. CREATE TABLE SQL 가져오기
        create_sql = get_create_table_sql(cursor, table_name)
        if not create_sql:
            print(f"오류: 테이블 '{table_name}'의 CREATE TABLE SQL을 가져올 수 없습니다.")
            conn.close()
            sys.exit(1)
        
        # 3. 임시 테이블명
        temp_table = f"{table_name}_temp_rename"
        
        # 4. 새 컬럼명으로 CREATE TABLE SQL 수정
        # 간단한 방법: 컬럼 리스트를 새로 생성
        column_defs = []
        for col in new_schema:
            col_def = f'"{col[1]}" {col[2]}'
            if col[3]:  # NOT NULL
                col_def += " NOT NULL"
            if col[4] is not None:  # DEFAULT
                col_def += f" DEFAULT {col[4]}"
            if col[5]:  # PRIMARY KEY
                col_def += " PRIMARY KEY"
            column_defs.append(col_def)
        
        # 5. 임시 테이블 생성
        create_temp_sql = f"CREATE TABLE {temp_table} ({', '.join(column_defs)})"
        cursor.execute(create_temp_sql)
        
        # 6. 데이터 복사
        # 새 테이블의 컬럼 순서대로 (이미 new_column으로 변경됨)
        new_column_list = [f'"{col[1]}"' for col in new_schema]
        # 기존 테이블의 컬럼 순서대로 (old_column 그대로)
        old_column_list = [f'"{col[1]}"' for col in schema]
        
        insert_sql = f"INSERT INTO {temp_table} ({', '.join(new_column_list)}) SELECT {', '.join(old_column_list)} FROM {table_name}"
        cursor.execute(insert_sql)
        
        # 7. 기존 테이블 삭제
        cursor.execute(f"DROP TABLE {table_name}")
        
        # 8. 임시 테이블을 원래 이름으로 변경
        cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
        
        conn.commit()
        print(f"✓ 컬럼명 변경 완료: '{table_name}.{old_column}' -> '{table_name}.{new_column}'")
        
    except sqlite3.Error as e:
        print(f"오류: 컬럼명 변경 실패 - {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='SQLite 데이터베이스의 테이블명과 컬럼명을 변경합니다.'
    )
    parser.add_argument('db_file', help='데이터베이스 파일 경로')
    parser.add_argument('--rename-table', nargs=2, metavar=('OLD_NAME', 'NEW_NAME'),
                       help='테이블명 변경: --rename-table old_name new_name')
    parser.add_argument('--rename-column', nargs=3, metavar=('TABLE', 'OLD_COLUMN', 'NEW_COLUMN'),
                       action='append',
                       help='컬럼명 변경: --rename-column table_name old_column new_column (여러 번 사용 가능)')
    
    args = parser.parse_args()
    
    if not args.rename_table and not args.rename_column:
        parser.print_help()
        print("\n오류: --rename-table 또는 --rename-column 옵션을 지정해야 합니다.")
        sys.exit(1)
    
    # 테이블명 변경
    if args.rename_table:
        old_name, new_name = args.rename_table
        rename_table(args.db_file, old_name, new_name)
    
    # 컬럼명 변경 (여러 개 가능)
    if args.rename_column:
        for table, old_col, new_col in args.rename_column:
            rename_column(args.db_file, table, old_col, new_col)


if __name__ == '__main__':
    main()

