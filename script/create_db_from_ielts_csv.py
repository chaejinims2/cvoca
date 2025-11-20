#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IELTS 단어장 CSV 파일들로부터 SQLite 데이터베이스를 생성하는 스크립트

사용법: python script/create_db_from_ielts_csv.py <output_db> [--overwrite]
예시: python script/create_db_from_ielts_csv.py data/ielts_voca_20_30.db
"""

import csv
import sqlite3
import sys
import os
from pathlib import Path


def create_database_from_csvs(output_db, csv_dir, overwrite=False):
    """
    CSV 파일들로부터 데이터베이스 생성
    
    Args:
        output_db: 출력 데이터베이스 파일 경로
        csv_dir: CSV 파일들이 있는 디렉토리 경로
        overwrite: 기존 DB 파일을 덮어쓸지 여부
    """
    csv_dir = Path(csv_dir)
    
    # CSV 파일 경로
    book_meta_csv = csv_dir / "book_meta.csv"
    words_csv = csv_dir / "words.csv"
    definitions_csv = csv_dir / "definitions.csv"
    examples_csv = csv_dir / "examples.csv"
    
    # CSV 파일 존재 확인
    csv_files = {
        'book_meta': book_meta_csv,
        'words': words_csv,
        'definitions': definitions_csv,
        'examples': examples_csv
    }
    
    for name, path in csv_files.items():
        if not path.exists():
            print(f"오류: CSV 파일 '{path}'을 찾을 수 없습니다.")
            sys.exit(1)
    
    # 출력 파일이 이미 존재하는지 확인
    if os.path.exists(output_db) and not overwrite:
        print(f"오류: 데이터베이스 파일 '{output_db}'이 이미 존재합니다.")
        print("      덮어쓰려면 --overwrite 옵션을 사용하세요.")
        sys.exit(1)
    
    # 기존 파일 삭제 (overwrite 옵션이 있으면)
    if os.path.exists(output_db) and overwrite:
        os.remove(output_db)
        print(f"기존 데이터베이스 파일 '{output_db}' 삭제됨")
    
    # 데이터베이스 연결
    conn = sqlite3.connect(output_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    print(f"새 데이터베이스 생성: {output_db}")
    print(f"CSV 디렉토리: {csv_dir}\n")
    
    # 1. books 테이블 생성 및 데이터 삽입
    print("=== books 테이블 생성 ===")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id                INTEGER PRIMARY KEY,
            code_name              TEXT    NOT NULL,
            max_days               INTEGER NOT NULL,
            max_words_per_day      INTEGER NOT NULL,
            max_senses_per_word    INTEGER NOT NULL,
            max_examples_per_sense INTEGER NOT NULL,
            created_at             TEXT    NOT NULL
        )
    """)
    
    with open(book_meta_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['book_id'].strip():  # 빈 행 건너뛰기
                cursor.execute("""
                    INSERT INTO books (
                        book_id, code_name, max_days, max_words_per_day,
                        max_senses_per_word, max_examples_per_sense, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row['book_id']),
                    row['code_name'],
                    int(row['max_days']),
                    int(row['max_words_per_day']),
                    int(row['max_senses_per_word']),
                    int(row['max_examples_per_sense']),
                    row['created_at']
                ))
    
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    print(f"  삽입된 행 수: {book_count}개\n")
    
    # 2. words 테이블 생성 및 데이터 삽입
    print("=== words 테이블 생성 ===")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            word_id INTEGER PRIMARY KEY,
            day_no  INTEGER NOT NULL,
            word_no INTEGER NOT NULL,
            word    TEXT    NOT NULL,
            UNIQUE (day_no, word_no)
        )
    """)
    
    with open(words_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if row['word_id'].strip():  # 빈 행 건너뛰기
                rows.append((
                    int(row['word_id']),
                    int(row['day_no']),
                    int(row['word_no']),
                    row['word']
                ))
        
        cursor.executemany("""
            INSERT INTO words (word_id, day_no, word_no, word)
            VALUES (?, ?, ?, ?)
        """, rows)
    
    cursor.execute("SELECT COUNT(*) FROM words")
    word_count = cursor.fetchone()[0]
    print(f"  삽입된 행 수: {word_count}개\n")
    
    # 3. definitions 테이블 생성 및 데이터 삽입
    print("=== definitions 테이블 생성 ===")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS definitions (
            definition_id  INTEGER PRIMARY KEY,
            word_id        INTEGER NOT NULL,
            sense_no       INTEGER NOT NULL,
            definition     TEXT    NOT NULL,
            part_of_speech TEXT,
            FOREIGN KEY (word_id) REFERENCES words(word_id),
            UNIQUE (word_id, sense_no)
        )
    """)
    
    with open(definitions_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if row['definition_id'].strip():  # 빈 행 건너뛰기
                part_of_speech = row['part_of_speech'] if row['part_of_speech'].strip() else None
                rows.append((
                    int(row['definition_id']),
                    int(row['word_id']),
                    int(row['sense_no']),
                    row['definition'],
                    part_of_speech
                ))
        
        cursor.executemany("""
            INSERT INTO definitions (
                definition_id, word_id, sense_no, definition, part_of_speech
            ) VALUES (?, ?, ?, ?, ?)
        """, rows)
    
    cursor.execute("SELECT COUNT(*) FROM definitions")
    def_count = cursor.fetchone()[0]
    print(f"  삽입된 행 수: {def_count}개\n")
    
    # 4. examples 테이블 생성 및 데이터 삽입
    print("=== examples 테이블 생성 ===")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS examples (
            example_id       INTEGER PRIMARY KEY,
            definition_id    INTEGER NOT NULL,
            example_no       INTEGER NOT NULL,
            example_sentence TEXT    NOT NULL,
            FOREIGN KEY (definition_id) REFERENCES definitions(definition_id),
            UNIQUE (definition_id, example_no)
        )
    """)
    
    with open(examples_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if row['example_id'].strip():  # 빈 행 건너뛰기
                rows.append((
                    int(row['example_id']),
                    int(row['definition_id']),
                    int(row['example_no']),
                    row['example_sentence']
                ))
        
        cursor.executemany("""
            INSERT INTO examples (
                example_id, definition_id, example_no, example_sentence
            ) VALUES (?, ?, ?, ?)
        """, rows)
    
    cursor.execute("SELECT COUNT(*) FROM examples")
    ex_count = cursor.fetchone()[0]
    print(f"  삽입된 행 수: {ex_count}개\n")
    
    # 변경사항 커밋
    conn.commit()
    
    # 최종 통계
    print("=== 생성 완료 ===")
    print(f"데이터베이스 파일: {output_db}")
    print(f"\n테이블별 행 수:")
    for table in ['books', 'words', 'definitions', 'examples']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count}개 행")
    
    # 인덱스 생성 (성능 향상)
    print("\n=== 인덱스 생성 ===")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_definitions_word_id ON definitions(word_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_examples_definition_id ON examples(definition_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_day_no ON words(day_no)")
    conn.commit()
    print("  인덱스 생성 완료")
    
    conn.close()
    print(f"\n데이터베이스 생성이 완료되었습니다: {output_db}")


def main():
    if len(sys.argv) < 2:
        print("사용법: python script/create_db_from_ielts_csv.py <output_db> [--overwrite]")
        print("예시: python script/create_db_from_ielts_csv.py data/ielts_voca_20_30.db")
        print("      python script/create_db_from_ielts_csv.py data/ielts_voca_20_30.db --overwrite")
        print("\n옵션:")
        print("  --overwrite: 기존 데이터베이스 파일을 덮어씁니다")
        print("\n참고: CSV 파일들은 output_db와 같은 디렉토리에 있어야 합니다.")
        print("      또는 CSV 디렉토리 경로를 지정할 수 있습니다.")
        sys.exit(1)
    
    # 인자 파싱
    args = sys.argv[1:]
    overwrite = '--overwrite' in args
    if overwrite:
        args.remove('--overwrite')
    
    output_db = Path(args[0])
    
    # CSV 디렉토리 결정: output_db와 같은 디렉토리 또는 명시적으로 지정
    if len(args) > 1:
        csv_dir = Path(args[1])
    else:
        csv_dir = output_db.parent
    
    create_database_from_csvs(output_db, csv_dir, overwrite)


if __name__ == "__main__":
    main()

