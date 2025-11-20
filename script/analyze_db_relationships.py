#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터베이스의 관계 구조와 데이터 무결성 분석
"""

import sqlite3
import sys
import os


def analyze_relationships(db_file):
    """
    데이터베이스의 관계 구조와 데이터 무결성 분석
    """
    if not os.path.exists(db_file):
        print(f"오류: 데이터베이스 파일 '{db_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("=" * 80)
    print(f"데이터베이스 관계 분석: {db_file}")
    print("=" * 80)
    
    # 테이블 목록
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n테이블: {', '.join(tables)}\n")
    
    # 각 테이블의 컬럼 정보
    table_columns = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        table_columns[table] = columns
        print(f"{table}: {', '.join(columns)}")
    
    print("\n" + "=" * 80)
    print("관계 분석")
    print("=" * 80)
    
    # Words 테이블 분석
    if 'Words' in tables:
        print("\n[Words 테이블]")
        cursor.execute("SELECT COUNT(DISTINCT word_id) FROM Words")
        unique_words = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Words")
        total_words = cursor.fetchone()[0]
        print(f"  총 행 수: {total_words}")
        print(f"  고유 word_id 수: {unique_words}")
        
        # day_no별 통계
        cursor.execute("SELECT day_no, COUNT(*) as cnt FROM Words GROUP BY day_no ORDER BY day_no")
        day_stats = cursor.fetchall()
        print(f"  day_no별 단어 수:")
        for day_id, cnt in day_stats[:10]:  # 처음 10개만
            print(f"    Day {day_id}: {cnt}개")
        if len(day_stats) > 10:
            print(f"    ... (총 {len(day_stats)}개 Day)")
    
    # Definitions 테이블 분석
    if 'Definitions' in tables:
        print("\n[Definitions 테이블]")
        # Definitions 테이블의 컬럼 정보 가져오기
        cursor.execute("PRAGMA table_info(Definitions)")
        def_columns = [col[1] for col in cursor.fetchall()]
        
        # definition_id 컬럼 찾기 (definition_id 또는 DefId)
        definition_id_col = None
        if 'definition_id' in def_columns:
            definition_id_col = 'definition_id'
        elif 'DefId' in def_columns:
            definition_id_col = 'DefId'
        
        cursor.execute("SELECT COUNT(*) FROM Definitions")
        total_defs = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT word_id) FROM Definitions")
        words_with_defs = cursor.fetchone()[0]
        
        if definition_id_col:
            cursor.execute(f"SELECT COUNT(DISTINCT {definition_id_col}) FROM Definitions")
            unique_defs = cursor.fetchone()[0]
        else:
            unique_defs = 0
        
        print(f"  총 행 수: {total_defs}")
        print(f"  정의가 있는 word_id 수: {words_with_defs}")
        if definition_id_col:
            print(f"  고유 {definition_id_col} 수: {unique_defs}")
        
        # word_id별 정의 수
        cursor.execute("""
            SELECT word_id, COUNT(*) as cnt 
            FROM Definitions 
            GROUP BY word_id 
            ORDER BY cnt DESC 
            LIMIT 10
        """)
        word_def_counts = cursor.fetchall()
        print(f"  정의가 많은 word_id (상위 10개):")
        for word_id, cnt in word_def_counts:
            print(f"    word_id {word_id}: {cnt}개 정의")
    
    # Examples 테이블 분석
    if 'Examples' in tables:
        print("\n[Examples 테이블]")
        # Examples 테이블의 컬럼 정보 가져오기
        cursor.execute("PRAGMA table_info(Examples)")
        ex_columns = [col[1] for col in cursor.fetchall()]
        
        # DefId 컬럼 찾기 (DefId 또는 definition_id)
        def_id_col = None
        if 'DefId' in ex_columns:
            def_id_col = 'DefId'
        elif 'definition_id' in ex_columns:
            def_id_col = 'definition_id'
        
        cursor.execute("SELECT COUNT(*) FROM Examples")
        total_examples = cursor.fetchone()[0]
        
        if def_id_col:
            cursor.execute(f"SELECT COUNT(DISTINCT {def_id_col}) FROM Examples")
            defs_with_examples = cursor.fetchone()[0]
        else:
            defs_with_examples = 0
        
        cursor.execute("SELECT COUNT(DISTINCT example_id) FROM Examples")
        unique_examples = cursor.fetchone()[0]
        
        print(f"  총 행 수: {total_examples}")
        if def_id_col:
            print(f"  예문이 있는 {def_id_col} 수: {defs_with_examples}")
        print(f"  고유 example_id 수: {unique_examples}")
    
    print("\n" + "=" * 80)
    print("데이터 무결성 검사")
    print("=" * 80)
    
    # Words와 Definitions 간 관계
    if 'Words' in tables and 'Definitions' in tables:
        print("\n[Words <-> Definitions 관계]")
        
        # Words 테이블의 컬럼 정보 가져오기
        cursor.execute("PRAGMA table_info(Words)")
        words_columns = [col[1] for col in cursor.fetchall()]
        word_col = 'Word' if 'Word' in words_columns else None
        
        # Definitions 테이블의 컬럼 정보 가져오기
        cursor.execute("PRAGMA table_info(Definitions)")
        def_columns = [col[1] for col in cursor.fetchall()]
        definition_col = 'definition' if 'definition' in def_columns else None
        
        # Words에 있지만 Definitions에 없는 word_id
        # (행이 없거나 TempWord/TempDefinition 포함)
        if word_col and definition_col:
            cursor.execute(f"""
                SELECT COUNT(DISTINCT w.word_id)
                FROM Words w
                LEFT JOIN Definitions d ON w.word_id = d.word_id
                WHERE d.word_id IS NULL 
                   OR w.{word_col} LIKE '%TempWord%'
                   OR (d.word_id IS NOT NULL AND d.{definition_col} LIKE '%TempDefinition%')
            """)
        else:
            cursor.execute("""
                SELECT COUNT(DISTINCT w.word_id)
                FROM Words w
                LEFT JOIN Definitions d ON w.word_id = d.word_id
                WHERE d.word_id IS NULL
            """)
        words_without_defs = cursor.fetchone()[0]
        print(f"  정의가 없는 word_id 수: {words_without_defs}")
        
        # Definitions에 있지만 Words에 없는 word_id
        # (행이 없거나 TempWord/TempDefinition 포함)
        if word_col and definition_col:
            cursor.execute(f"""
                SELECT COUNT(DISTINCT d.word_id)
                FROM Definitions d
                LEFT JOIN Words w ON d.word_id = w.word_id
                WHERE w.word_id IS NULL 
                   OR d.{definition_col} LIKE '%TempDefinition%'
                   OR (w.word_id IS NOT NULL AND w.{word_col} LIKE '%TempWord%')
            """)
        else:
            cursor.execute("""
                SELECT COUNT(DISTINCT d.word_id)
                FROM Definitions d
                LEFT JOIN Words w ON d.word_id = w.word_id
                WHERE w.word_id IS NULL
            """)
        defs_without_words = cursor.fetchone()[0]
        print(f"  Words에 없는 word_id (Definitions): {defs_without_words}")
    
    # Definitions와 Examples 간 관계
    if 'Definitions' in tables and 'Examples' in tables:
        print("\n[Definitions <-> Examples 관계]")
        
        # 컬럼명 동적 감지
        cursor.execute("PRAGMA table_info(Definitions)")
        def_columns = [col[1] for col in cursor.fetchall()]
        definition_col = 'definition' if 'definition' in def_columns else None
        
        cursor.execute("PRAGMA table_info(Examples)")
        ex_columns = [col[1] for col in cursor.fetchall()]
        
        # Definitions의 ID 컬럼 찾기
        def_def_id_col = None
        if 'definition_id' in def_columns:
            def_def_id_col = 'definition_id'
        elif 'DefId' in def_columns:
            def_def_id_col = 'DefId'
        
        # Examples의 ID 컬럼 찾기
        ex_def_id_col = None
        if 'DefId' in ex_columns:
            ex_def_id_col = 'DefId'
        elif 'definition_id' in ex_columns:
            ex_def_id_col = 'definition_id'
        
        if def_def_id_col and ex_def_id_col:
            # example_sentence 컬럼 찾기
            example_sentence_col = 'example_sentence' if 'example_sentence' in ex_columns else None
            
            # Definitions에 있지만 Examples에 없는 ID
            # (행이 없거나 TempDefinition/TempExample 포함)
            if definition_col and example_sentence_col:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT d.{def_def_id_col})
                    FROM Definitions d
                    LEFT JOIN Examples e ON d.{def_def_id_col} = e.{ex_def_id_col}
                    WHERE e.{ex_def_id_col} IS NULL 
                       OR d.{definition_col} LIKE '%TempDefinition%'
                       OR (e.{ex_def_id_col} IS NOT NULL AND e.{example_sentence_col} LIKE '%TempExample%')
                """)
            else:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT d.{def_def_id_col})
                    FROM Definitions d
                    LEFT JOIN Examples e ON d.{def_def_id_col} = e.{ex_def_id_col}
                    WHERE e.{ex_def_id_col} IS NULL
                """)
            defs_without_examples = cursor.fetchone()[0]
            print(f"  예문이 없는 {def_def_id_col} 수: {defs_without_examples}")
            
            # Examples에 있지만 Definitions에 없는 ID
            # (행이 없거나 TempDefinition/TempExample 포함)
            if definition_col and example_sentence_col:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT e.{ex_def_id_col})
                    FROM Examples e
                    LEFT JOIN Definitions d ON e.{ex_def_id_col} = d.{def_def_id_col}
                    WHERE d.{def_def_id_col} IS NULL 
                       OR e.{example_sentence_col} LIKE '%TempExample%'
                       OR (d.{def_def_id_col} IS NOT NULL AND d.{definition_col} LIKE '%TempDefinition%')
                """)
            else:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT e.{ex_def_id_col})
                    FROM Examples e
                    LEFT JOIN Definitions d ON e.{ex_def_id_col} = d.{def_def_id_col}
                    WHERE d.{def_def_id_col} IS NULL
                """)
            examples_without_defs = cursor.fetchone()[0]
            print(f"  Definitions에 없는 {ex_def_id_col} (Examples): {examples_without_defs}")
        else:
            print("  경고: Definitions와 Examples 간 관계를 확인할 수 없습니다 (ID 컬럼을 찾을 수 없음)")
    
    # 전체 관계 체인 검사
    if all(t in tables for t in ['Words', 'Definitions', 'Examples']):
        print("\n[전체 관계 체인 검사]")
        
        # 컬럼명 동적 감지
        cursor.execute("PRAGMA table_info(Words)")
        words_columns = [col[1] for col in cursor.fetchall()]
        word_col = 'Word' if 'Word' in words_columns else None
        
        cursor.execute("PRAGMA table_info(Definitions)")
        def_columns = [col[1] for col in cursor.fetchall()]
        definition_col = 'definition' if 'definition' in def_columns else None
        
        cursor.execute("PRAGMA table_info(Examples)")
        ex_columns = [col[1] for col in cursor.fetchall()]
        example_sentence_col = 'example_sentence' if 'example_sentence' in ex_columns else None
        
        # Definitions의 ID 컬럼 찾기
        def_def_id_col = None
        if 'definition_id' in def_columns:
            def_def_id_col = 'definition_id'
        elif 'DefId' in def_columns:
            def_def_id_col = 'DefId'
        
        # Examples의 ID 컬럼 찾기
        ex_def_id_col = None
        if 'DefId' in ex_columns:
            ex_def_id_col = 'DefId'
        elif 'definition_id' in ex_columns:
            ex_def_id_col = 'definition_id'
        
        if def_def_id_col and ex_def_id_col:
            # 완전한 체인 (Words -> Definitions -> Examples)
            # TempWord/TempDefinition/TempExample 제외
            if word_col and definition_col and example_sentence_col:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT w.word_id)
                    FROM Words w
                    INNER JOIN Definitions d ON w.word_id = d.word_id
                    INNER JOIN Examples e ON d.{def_def_id_col} = e.{ex_def_id_col}
                    WHERE w.{word_col} NOT LIKE '%TempWord%'
                      AND d.{definition_col} NOT LIKE '%TempDefinition%'
                      AND e.{example_sentence_col} NOT LIKE '%TempExample%'
                """)
            else:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT w.word_id)
                    FROM Words w
                    INNER JOIN Definitions d ON w.word_id = d.word_id
                    INNER JOIN Examples e ON d.{def_def_id_col} = e.{ex_def_id_col}
                """)
            complete_chains = cursor.fetchone()[0]
            print(f"  완전한 체인 (Words -> Definitions -> Examples): {complete_chains}개 word_id")
            
            # Words -> Definitions만 있는 경우
            # (예문이 없거나 TempExample 포함)
            if word_col and definition_col and example_sentence_col:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT w.word_id)
                    FROM Words w
                    INNER JOIN Definitions d ON w.word_id = d.word_id
                    LEFT JOIN Examples e ON d.{def_def_id_col} = e.{ex_def_id_col}
                    WHERE w.{word_col} NOT LIKE '%TempWord%'
                      AND d.{definition_col} NOT LIKE '%TempDefinition%'
                      AND (e.{ex_def_id_col} IS NULL OR e.{example_sentence_col} LIKE '%TempExample%')
                """)
            else:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT w.word_id)
                    FROM Words w
                    INNER JOIN Definitions d ON w.word_id = d.word_id
                    LEFT JOIN Examples e ON d.{def_def_id_col} = e.{ex_def_id_col}
                    WHERE e.{ex_def_id_col} IS NULL
                """)
            words_defs_only = cursor.fetchone()[0]
            print(f"  Words -> Definitions만 (예문 없음): {words_defs_only}개 word_id")
        else:
            print("  경고: 전체 관계 체인을 확인할 수 없습니다 (ID 컬럼을 찾을 수 없음)")
    
    # ID 범위 확인
    print("\n" + "=" * 80)
    print("ID 범위 확인")
    print("=" * 80)
    
    for table in tables:
        # Id로 끝나는 컬럼 찾기
        id_columns = [col for col in table_columns[table] if col.endswith('Id')]
        if id_columns:
            print(f"\n[{table}]")
            for id_col in id_columns:
                cursor.execute(f"SELECT MIN({id_col}), MAX({id_col}), COUNT(DISTINCT {id_col}) FROM {table}")
                min_val, max_val, distinct_count = cursor.fetchone()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_count = cursor.fetchone()[0]
                print(f"  {id_col}: 범위 [{min_val} ~ {max_val}], 고유값 {distinct_count}개 / 총 {total_count}개 행")
    
    conn.close()
    print("\n" + "=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/analyze_db_relationships.py <db_file>")
        sys.exit(1)
    
    db_file = sys.argv[1]
    analyze_relationships(db_file)

