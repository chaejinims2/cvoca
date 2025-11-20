# script/init_db.py

import sys
import sqlite3
from pathlib import Path
import csv
from datetime import datetime

# ---- Cvoca 설계 상수 (불변) ----
MAX_SENSES_PER_WORD    = 10  # 기존 MAX_MEAN_BY_WORD
MAX_EXAMPLES_PER_SENSE = 10  # 기존 MAX_USE_BY_DEF


# ---- ID 계산 함수 ----
def calc_word_id(day_no: int, word_no: int, max_word_num: int) -> int:
    """
    전역 word_id 계산:
    word_id = (day_no - 1) * MAX_WORDS_PER_DAY + word_no
    """
    return (day_no - 1) * max_word_num + word_no


def calc_definition_id(word_id: int, sense_no: int) -> int:
    """
    전역 definition_id 계산:
    definition_id = word_id * MAX_SENSES_PER_WORD + sense_no
    """
    return word_id * MAX_SENSES_PER_WORD + sense_no


def calc_example_id(definition_id: int, example_no: int) -> int:
    """
    전역 example_id 계산:
    example_id = definition_id * MAX_EXAMPLES_PER_SENSE + example_no
    """
    return definition_id * MAX_EXAMPLES_PER_SENSE + example_no


# ---- DB 초기 스키마 + books 메타 정보 ----
def init_db(db_path: Path, basebook: str, max_days: int, max_words: int) -> sqlite3.Connection:
    """
    DB 파일을 생성/연결하고, 스키마 및 books 메타 정보를 초기화한다.
    """
    conn = sqlite3.connect(db_path)
    # SQLite에서 FK 제약 활성화
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # 스키마 생성
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS books (
        book_id                INTEGER PRIMARY KEY,
        code_name              TEXT    NOT NULL,
        max_days               INTEGER NOT NULL,
        max_words_per_day      INTEGER NOT NULL,
        max_senses_per_word    INTEGER NOT NULL,
        max_examples_per_sense INTEGER NOT NULL,
        created_at             TEXT    NOT NULL
    );

    CREATE TABLE IF NOT EXISTS words (
        word_id INTEGER PRIMARY KEY,
        day_no  INTEGER NOT NULL,
        word_no INTEGER NOT NULL,
        word    TEXT    NOT NULL,
        UNIQUE (day_no, word_no)
    );

    CREATE TABLE IF NOT EXISTS definitions (
        definition_id  INTEGER PRIMARY KEY,
        word_id        INTEGER NOT NULL,
        sense_no       INTEGER NOT NULL,
        definition     TEXT    NOT NULL,
        part_of_speech TEXT,
        FOREIGN KEY (word_id) REFERENCES words(word_id),
        UNIQUE (word_id, sense_no)
    );

    CREATE TABLE IF NOT EXISTS examples (
        example_id       INTEGER PRIMARY KEY,
        definition_id    INTEGER NOT NULL,
        example_no       INTEGER NOT NULL,
        example_sentence TEXT    NOT NULL,
        FOREIGN KEY (definition_id) REFERENCES definitions(definition_id),
        UNIQUE (definition_id, example_no)
    );
    """)

    # books 테이블 1행 upsert (재실행 시에도 갱신되도록)
    created_at = datetime.utcnow().isoformat(timespec="seconds")
    cur.execute("""
        INSERT INTO books (
            book_id,
            code_name,
            max_days,
            max_words_per_day,
            max_senses_per_word,
            max_examples_per_sense,
            created_at
        )
        VALUES (1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(book_id) DO UPDATE SET
            code_name              = excluded.code_name,
            max_days               = excluded.max_days,
            max_words_per_day      = excluded.max_words_per_day,
            max_senses_per_word    = excluded.max_senses_per_word,
            max_examples_per_sense = excluded.max_examples_per_sense,
            created_at             = excluded.created_at;
    """, (
        basebook,
        max_days,
        max_words,
        MAX_SENSES_PER_WORD,
        MAX_EXAMPLES_PER_SENSE,
        created_at,
    ))

    conn.commit()
    return conn


# ---- 초기 데이터 생성 ----
def populate_initial_data(conn: sqlite3.Connection, max_days: int, max_words: int) -> None:
    """
    words / definitions / examples 테이블에
    Temp* 형태의 초기 데이터를 넣는다.

    - 이미 words에 데이터가 있으면 RuntimeError 발생시켜 재초기화를 막는다.
    """
    cur = conn.cursor()

    # 이미 초기화된 DB인지 검사
    row = cur.execute("SELECT COUNT(*) FROM words").fetchone()
    if row and row[0] > 0:
        raise RuntimeError(
            "words 테이블에 이미 데이터가 존재합니다. "
            "기존 DB를 유지하려면 init 스크립트를 다시 실행하지 마세요. "
            "완전 재생성을 원하면 DB 파일을 삭제한 뒤 다시 실행하십시오."
        )

    # 트랜잭션 명시적으로 시작
    cur.execute("BEGIN")

    try:
        # 1) words 테이블 초기화
        for day_no in range(1, max_days + 1):
            for word_no in range(1, max_words + 1):
                word_id = calc_word_id(day_no, word_no, max_words)
                temp_word = f"TempWord_{word_id}"
                cur.execute(
                    "INSERT INTO words (word_id, day_no, word_no, word) "
                    "VALUES (?, ?, ?, ?)",
                    (word_id, day_no, word_no, temp_word)
                )

        # 2) definitions 테이블 초기 기본 행: sense_no=0만 생성
        #    (총 개수 = max_days * max_words)
        for day_no in range(1, max_days + 1):
            for word_no in range(1, max_words + 1):
                word_id = calc_word_id(day_no, word_no, max_words)
                sense_no = 0
                definition_id = calc_definition_id(word_id, sense_no)
                temp_def = f"TempDefinition_{definition_id}"
                cur.execute(
                    "INSERT INTO definitions (definition_id, word_id, sense_no, definition, part_of_speech) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (definition_id, word_id, sense_no, temp_def, None)
                )

        # 3) examples 테이블 초기 기본 행: example_no=0만 생성
        for day_no in range(1, max_days + 1):
            for word_no in range(1, max_words + 1):
                word_id = calc_word_id(day_no, word_no, max_words)
                sense_no = 0
                definition_id = calc_definition_id(word_id, sense_no)
                example_no = 0
                example_id = calc_example_id(definition_id, example_no)
                temp_ex = f"TempExample_{example_id}"
                cur.execute(
                    "INSERT INTO examples (example_id, definition_id, example_no, example_sentence) "
                    "VALUES (?, ?, ?, ?)",
                    (example_id, definition_id, example_no, temp_ex)
                )

    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


# ---- CSV export ----
def export_to_csv(conn: sqlite3.Connection, base_dir: Path) -> None:
    """
    words / definitions / examples 테이블과 books 메타를
    CSV 형태로 내보내고, user/ 하위에 작업용 복사본을 생성한다.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    user_dir = base_dir / "user"
    user_dir.mkdir(exist_ok=True)

    cur = conn.cursor()

    # 0) books (선택 사항이지만, 책 스펙을 보기 좋게 별도 CSV로 둠)
    rows = cur.execute(
        "SELECT book_id, code_name, max_days, max_words_per_day, "
        "max_senses_per_word, max_examples_per_sense, created_at "
        "FROM books WHERE book_id = 1"
    ).fetchall()

    with open(base_dir / "book_meta.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "book_id",
            "code_name",
            "max_days",
            "max_words_per_day",
            "max_senses_per_word",
            "max_examples_per_sense",
            "created_at",
        ])
        writer.writerows(rows)

    # 1) words
    rows = cur.execute(
        "SELECT word_id, day_no, word_no, word FROM words"
    ).fetchall()
    words_csv = base_dir / "words.csv"
    with open(words_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word_id", "day_no", "word_no", "word"])
        writer.writerows(rows)
    # user 복사본
    (user_dir / "words.csv").write_text(words_csv.read_text(encoding="utf-8"), encoding="utf-8")

    # 2) definitions
    rows = cur.execute(
        "SELECT definition_id, word_id, sense_no, definition, part_of_speech "
        "FROM definitions"
    ).fetchall()
    defs_csv = base_dir / "definitions.csv"
    with open(defs_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["definition_id", "word_id", "sense_no", "definition", "part_of_speech"])
        writer.writerows(rows)
    (user_dir / "definitions.csv").write_text(defs_csv.read_text(encoding="utf-8"), encoding="utf-8")

    # 3) examples
    rows = cur.execute(
        "SELECT example_id, definition_id, example_no, example_sentence "
        "FROM examples"
    ).fetchall()
    ex_csv = base_dir / "examples.csv"
    with open(ex_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["example_id", "definition_id", "example_no", "example_sentence"])
        writer.writerows(rows)
    (user_dir / "examples.csv").write_text(ex_csv.read_text(encoding="utf-8"), encoding="utf-8")


# ---- main ----
def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python script/init_db.py <BASEBOOK_NAME> <MAX_DAYS_NUM> <MAX_WORD_NUM>")
        sys.exit(1)

    basebook = sys.argv[1]
    max_days = int(sys.argv[2])
    max_words = int(sys.argv[3])

    book_id = f"{basebook}_{max_days}_{max_words}"
    data_dir = Path("data")
    db_path = data_dir / f"{book_id}.db"
    book_dir = data_dir / book_id

    data_dir.mkdir(exist_ok=True)

    conn = init_db(db_path, basebook, max_days, max_words)
    populate_initial_data(conn, max_days, max_words)
    export_to_csv(conn, book_dir)
    conn.close()


if __name__ == "__main__":
    main()