#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터베이스 구조와 내용을 리뷰하는 스크립트
"""

import sqlite3
import sys
import os


def review_database(db_file):
    """
    데이터베이스의 구조와 내용을 상세히 리뷰
    
    Args:
        db_file: SQLite 데이터베이스 파일 경로
    """
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("=" * 80)
    print(f"데이터베이스 리뷰: {db_file}")
    print("=" * 80)
    
    # 파일 크기
    file_size = os.path.getsize(db_file)
    print(f"\n파일 크기: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    
    # 모든 테이블 목록
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    if not tables:
        print("\n경고: 데이터베이스에 테이블이 없습니다.")
        conn.close()
        return
    
    print(f"\n테이블 수: {len(tables)}개")
    print("\n" + "=" * 80)
    
    # 각 테이블 상세 정보
    for idx, (table_name,) in enumerate(tables, 1):
        print(f"\n[{idx}/{len(tables)}] 테이블: {table_name}")
        print("-" * 80)
        
        # 테이블 스키마
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        
        print("\n컬럼 정보:")
        print(f"{'순서':<6} {'컬럼명':<25} {'타입':<15} {'NOT NULL':<10} {'기본값':<15} {'PK'}")
        print("-" * 80)
        
        primary_keys = []
        for col in schema:
            cid, name, col_type, notnull, default_val, pk = col
            pk_str = "✓" if pk else ""
            notnull_str = "✓" if notnull else ""
            default_str = str(default_val) if default_val is not None else ""
            
            print(f"{cid:<6} {name:<25} {col_type:<15} {notnull_str:<10} {default_str:<15} {pk_str}")
            
            if pk:
                primary_keys.append(name)
        
        if primary_keys:
            print(f"\nPrimary Key: {', '.join(primary_keys)}")
        
        # 행 수
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"\n총 행 수: {row_count:,}개")
        
        # 샘플 데이터 (최대 5행)
        if row_count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_rows = cursor.fetchall()
            
            print(f"\n샘플 데이터 (최대 5행):")
            column_names = [col[1] for col in schema]
            
            # 헤더 출력
            header = " | ".join([f"{name:<20}" for name in column_names[:5]])  # 최대 5개 컬럼만
            if len(column_names) > 5:
                header += " | ..."
            print(header)
            print("-" * min(120, len(header)))
            
            # 데이터 출력
            for row in sample_rows:
                row_str = " | ".join([f"{str(val)[:20]:<20}" if val is not None else f"{'NULL':<20}" for val in row[:5]])
                if len(row) > 5:
                    row_str += " | ..."
                print(row_str)
        
        # 인덱스 정보
        cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL", (table_name,))
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"\n인덱스 ({len(indexes)}개):")
            for idx_name, idx_sql in indexes:
                print(f"  - {idx_name}")
                if idx_sql:
                    print(f"    {idx_sql}")
        
        # 외래키 정보 (SQLite 3.6.19+)
        try:
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print(f"\n외래키 ({len(foreign_keys)}개):")
                for fk in foreign_keys:
                    # fk 구조: (id, seq, table, from, to, on_update, on_delete, match)
                    fk_table = fk[2]
                    fk_from = fk[3]
                    fk_to = fk[4]
                    print(f"  - {fk_from} -> {fk_table}.{fk_to}")
        except:
            pass  # 외래키 정보를 가져올 수 없는 경우 무시
        
        # 통계 정보
        if row_count > 0:
            # NULL 값이 있는 컬럼 확인
            null_counts = {}
            for col in schema:
                col_name = col[1]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
                null_count = cursor.fetchone()[0]
                if null_count > 0:
                    null_counts[col_name] = null_count
            
            if null_counts:
                print(f"\nNULL 값이 있는 컬럼:")
                for col_name, null_count in null_counts.items():
                    percentage = (null_count / row_count) * 100
                    print(f"  - {col_name}: {null_count:,}개 ({percentage:.1f}%)")
    
    # 전체 통계
    print("\n" + "=" * 80)
    print("전체 통계")
    print("=" * 80)
    
    total_rows = 0
    for (table_name,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        total_rows += row_count
        print(f"  {table_name}: {row_count:,}개 행")
    
    print(f"\n총 행 수: {total_rows:,}개")
    
    conn.close()
    print("\n" + "=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/review_db.py <db_file>")
        print("예시: python script/review_db.py data/vocabulary.db")
        sys.exit(1)
    
    db_file = sys.argv[1]
    review_database(db_file)

