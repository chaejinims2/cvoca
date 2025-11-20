#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 데이터베이스에 Primary Key와 Foreign Key 제약을 추가하는 스크립트
CSV 기반 워크플로우를 고려하여 안전하게 제약을 추가합니다.

사용법: python script/add_constraints_to_db.py <db_file> [--add-fk]
예시: python script/add_constraints_to_db.py vocabulary.db
      python script/add_constraints_to_db.py vocabulary.db --add-fk
"""

import sqlite3
import sys
import os


def get_table_schema(cursor, table_name):
    """
    테이블의 스키마 정보 가져오기
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()


def get_primary_key(cursor, table_name):
    """
    테이블의 Primary Key 컬럼 찾기
    """
    schema = get_table_schema(cursor, table_name)
    pk_columns = [col[1] for col in schema if col[5]]  # col[5]는 pk 플래그
    return pk_columns


def add_primary_key(cursor, table_name, pk_column):
    """
    테이블에 Primary Key 제약 추가 (테이블 재생성 필요)
    
    Args:
        cursor: 데이터베이스 커서
        table_name: 테이블명
        pk_column: Primary Key로 설정할 컬럼명
    """
    # 기존 스키마 가져오기
    schema = get_table_schema(cursor, table_name)
    
    # 이미 Primary Key가 있는지 확인
    existing_pk = get_primary_key(cursor, table_name)
    if existing_pk:
        if pk_column in existing_pk:
            print(f"  Primary Key '{pk_column}'가 이미 설정되어 있습니다.")
            return False
        else:
            print(f"  경고: 이미 다른 Primary Key가 있습니다: {existing_pk}")
            return False
    
    # 데이터 가져오기
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    column_names = [col[1] for col in schema]
    
    # Primary Key 컬럼이 존재하는지 확인
    if pk_column not in column_names:
        print(f"  오류: 컬럼 '{pk_column}'가 테이블에 없습니다.")
        return False
    
    # Primary Key 컬럼의 중복 확인
    cursor.execute(f"SELECT {pk_column}, COUNT(*) FROM {table_name} GROUP BY {pk_column} HAVING COUNT(*) > 1")
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"  오류: Primary Key 컬럼 '{pk_column}'에 중복 값이 있습니다:")
        for val, count in duplicates[:5]:
            print(f"    {val}: {count}개")
        if len(duplicates) > 5:
            print(f"    ... (총 {len(duplicates)}개 중복)")
        return False
    
    # NULL 값 확인
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {pk_column} IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        print(f"  오류: Primary Key 컬럼 '{pk_column}'에 NULL 값이 {null_count}개 있습니다.")
        return False
    
    try:
        # 임시 테이블명
        temp_table = f"{table_name}_temp_pk"
        
        # 새 스키마 생성 (Primary Key 추가)
        column_defs = []
        for col in schema:
            cid, name, col_type, notnull, default_val, pk = col
            col_def = f'"{name}" {col_type}'
            if notnull:
                col_def += " NOT NULL"
            if default_val is not None:
                col_def += f" DEFAULT {default_val}"
            if name == pk_column:
                col_def += " PRIMARY KEY"
            column_defs.append(col_def)
        
        # 임시 테이블 생성
        create_sql = f"CREATE TABLE {temp_table} ({', '.join(column_defs)})"
        cursor.execute(create_sql)
        
        # 데이터 복사
        column_list = ','.join([f'"{col[1]}"' for col in schema])
        insert_sql = f"INSERT INTO {temp_table} ({column_list}) SELECT {column_list} FROM {table_name}"
        cursor.execute(insert_sql)
        
        # 기존 테이블 삭제
        cursor.execute(f"DROP TABLE {table_name}")
        
        # 임시 테이블을 원래 이름으로 변경
        cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
        
        print(f"  ✓ Primary Key '{pk_column}' 추가 완료")
        return True
        
    except sqlite3.Error as e:
        print(f"  오류: Primary Key 추가 실패 - {e}")
        return False


def detect_primary_key(cursor, table_name):
    """
    테이블에서 Primary Key로 적합한 컬럼 자동 감지
    규칙: 테이블명에서 끝의 's'를 제거하고 'Id'를 추가
    """
    schema = get_table_schema(cursor, table_name)
    column_names = [col[1] for col in schema]
    
    # 이미 Primary Key가 있으면 반환
    existing_pk = get_primary_key(cursor, table_name)
    if existing_pk:
        return existing_pk[0]
    
    # 규칙: 테이블명에서 끝의 's'를 제거하고 'Id'를 추가
    # 예: Words -> word_id, Examples -> example_id, Definitions -> definition_id
    if table_name.endswith('s'):
        singular_name = table_name[:-1]  # 끝의 's' 제거
        expected_pk = f"{singular_name}Id"
    else:
        expected_pk = f"{table_name}Id"
    
    # 예상된 Primary Key 컬럼이 존재하는지 확인
    if expected_pk in column_names:
        return expected_pk
    
    # 없으면 Id로 끝나는 컬럼 중 가장 짧은 것 선택
    id_columns = [col for col in column_names if col.endswith('Id')]
    if id_columns:
        return min(id_columns, key=len)
    
    return None


def detect_foreign_keys(cursor, tables):
    """
    테이블 간 Foreign Key 관계 자동 감지
    """
    foreign_keys = []
    
    # 각 테이블의 컬럼 정보 수집
    table_info = {}
    for table_name in tables:
        schema = get_table_schema(cursor, table_name)
        table_info[table_name] = {
            'columns': [col[1] for col in schema],
            'pk': get_primary_key(cursor, table_name)
        }
    
    # Foreign Key 후보 찾기 (다른 테이블의 PK를 참조하는 컬럼)
    for table_name in tables:
        schema = get_table_schema(cursor, table_name)
        for col in schema:
            col_name = col[1]
            # Id로 끝나는 컬럼이 다른 테이블의 PK와 일치하는지 확인
            if col_name.endswith('Id') and col_name not in table_info[table_name]['pk']:
                # 참조할 수 있는 테이블 찾기
                for ref_table in tables:
                    if ref_table == table_name:
                        continue
                    
                    ref_pk = table_info[ref_table]['pk']
                    if ref_pk:
                        # 컬럼명이 테이블명 + Id 패턴인지 확인
                        # 예: word_id -> Words 테이블의 word_id
                        ref_table_singular = ref_table.rstrip('s')  # Words -> Word
                        if col_name == f"{ref_table_singular}Id" or col_name in ref_pk:
                            foreign_keys.append({
                                'table': table_name,
                                'column': col_name,
                                'ref_table': ref_table,
                                'ref_column': ref_pk[0]
                            })
    
    return foreign_keys


def add_foreign_key(cursor, table_name, column, ref_table, ref_column):
    """
    Foreign Key 제약 추가 (SQLite는 제한적 지원)
    참고: SQLite는 ALTER TABLE로 FK를 추가할 수 없으므로 테이블 재생성 필요
    """
    # SQLite에서 Foreign Key 활성화
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # 참조 무결성 확인
    cursor.execute(f"""
        SELECT COUNT(*) FROM {table_name} t
        LEFT JOIN {ref_table} r ON t.{column} = r.{ref_column}
        WHERE t.{column} IS NOT NULL AND r.{ref_column} IS NULL
    """)
    orphan_count = cursor.fetchone()[0]
    
    if orphan_count > 0:
        print(f"  경고: {orphan_count}개의 무효한 참조가 있습니다. Foreign Key를 추가할 수 없습니다.")
        return False
    
    # SQLite는 ALTER TABLE로 FK를 추가할 수 없으므로
    # 테이블 재생성이 필요하지만, 이는 복잡하므로 경고만 출력
    print(f"  참고: SQLite는 ALTER TABLE로 Foreign Key를 추가할 수 없습니다.")
    print(f"        Foreign Key 제약을 추가하려면 테이블을 재생성해야 합니다.")
    print(f"        관계는 데이터 무결성 검사로 확인할 수 있습니다.")
    return False


def add_constraints_to_database(db_file, add_foreign_keys=False):
    """
    데이터베이스에 Primary Key와 Foreign Key 제약 추가
    """
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("=" * 80)
    print(f"제약 조건 추가: {db_file}")
    print("=" * 80)
    
    # 테이블 목록
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    if not tables:
        print("경고: 데이터베이스에 테이블이 없습니다.")
        conn.close()
        return
    
    print(f"\n테이블 수: {len(tables)}개\n")
    
    # Primary Key 추가
    print("=" * 80)
    print("Primary Key 추가")
    print("=" * 80)
    
    pk_added = 0
    for table_name in tables:
        print(f"\n[{table_name}]")
        pk_column = detect_primary_key(cursor, table_name)
        
        if not pk_column:
            print(f"  Primary Key로 적합한 컬럼을 찾을 수 없습니다.")
            continue
        
        if add_primary_key(cursor, table_name, pk_column):
            pk_added += 1
            conn.commit()
    
    # Foreign Key 감지 및 정보 출력
    if add_foreign_keys:
        print("\n" + "=" * 80)
        print("Foreign Key 관계 감지")
        print("=" * 80)
        
        fk_relations = detect_foreign_keys(cursor, tables)
        
        if fk_relations:
            print(f"\n감지된 Foreign Key 관계 ({len(fk_relations)}개):")
            for fk in fk_relations:
                print(f"  {fk['table']}.{fk['column']} -> {fk['ref_table']}.{fk['ref_column']}")
            
            print("\n참고: SQLite는 ALTER TABLE로 Foreign Key를 추가할 수 없습니다.")
            print("      Foreign Key 제약을 추가하려면 테이블을 재생성해야 합니다.")
            print("      현재는 데이터 무결성 검사로 관계를 확인할 수 있습니다.")
        else:
            print("\nForeign Key 관계를 감지할 수 없습니다.")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("완료")
    print("=" * 80)
    print(f"Primary Key 추가: {pk_added}개 테이블")


def main():
    if len(sys.argv) < 2:
        print("사용법: python script/add_constraints_to_db.py <db_file> [--add-fk]")
        print("예시: python script/add_constraints_to_db.py vocabulary.db")
        print("      python script/add_constraints_to_db.py vocabulary.db --add-fk")
        print("\n옵션:")
        print("  --add-fk: Foreign Key 관계를 감지하고 정보를 출력합니다")
        sys.exit(1)
    
    db_file = sys.argv[1]
    add_fk = '--add-fk' in sys.argv
    
    add_constraints_to_database(db_file, add_fk)


if __name__ == "__main__":
    main()

