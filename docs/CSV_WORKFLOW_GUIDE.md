# CSV 기반 데이터베이스 워크플로우 가이드

이 문서는 CSV 파일을 사용하여 데이터베이스를 관리하는 워크플로우를 설명합니다.

## 개요

이 프로젝트는 CSV 파일을 중심으로 데이터를 관리하고, 필요할 때 SQLite 데이터베이스로 변환하는 워크플로우를 지원합니다.

### 주요 특징

- **CSV 우선**: 데이터는 CSV 파일로 관리
- **자동 변환**: 스크립트를 통해 CSV ↔ DB 변환
- **Primary Key 자동 감지**: Id로 끝나는 컬럼을 자동으로 Primary Key로 설정
- **유연한 스키마**: CSV 구조 변경 시 자동 반영

---

## 워크플로우

### 1. CSV 파일로부터 새 데이터베이스 생성

여러 CSV 파일로부터 새로운 데이터베이스를 생성합니다.

```bash
python script/create_db_from_csv.py <output_db> <csv_file1> [csv_file2] ...
```

**예시:**
```bash
# 여러 CSV 파일로부터 새 DB 생성
python script/create_db_from_csv.py data/vocabulary.db data/Words.csv data/Definitions.csv data/Examples.csv

# 기존 DB 덮어쓰기
python script/create_db_from_csv.py data/vocabulary.db data/*.csv --overwrite
```

**특징:**
- 각 CSV 파일명이 테이블명이 됩니다 (확장자 제외)
- Primary Key 자동 감지 (테이블명Id 또는 Id로 끝나는 컬럼)
- 데이터 타입 자동 추론

---

### 2. CSV 파일로 기존 데이터베이스 업데이트

기존 데이터베이스에 CSV 파일의 데이터를 추가하거나 업데이트합니다.

```bash
python script/import_csv_to_db.py <csv_file> <db_file> [-rf]
```

**예시:**
```bash
# CSV 데이터 추가 (중복 시 건너뛰기)
python script/import_csv_to_db.py data/Words.csv data/vocabulary.db

# CSV 데이터 추가 (중복 시 덮어쓰기)
python script/import_csv_to_db.py data/Words.csv data/vocabulary.db -rf
```

**특징:**
- Primary Key 기반 중복 체크
- `-rf` 옵션: 중복 시 기존 데이터 업데이트
- 컬럼명 자동 매핑 (대소문자 무시, 특수 매핑 규칙)

---

### 3. 데이터베이스에서 CSV 파일로 내보내기

데이터베이스의 모든 테이블을 각각 CSV 파일로 내보냅니다.

```bash
python script/export_all_tables_to_csv.py <db_file> [output_dir] [--overwrite]
```

**예시:**
```bash
# 모든 테이블을 output 폴더에 내보내기
python script/export_all_tables_to_csv.py data/vocabulary.db

# 지정한 디렉토리에 내보내기
python script/export_all_tables_to_csv.py data/vocabulary.db data/csv_exports

# 기존 파일 덮어쓰기
python script/export_all_tables_to_csv.py data/vocabulary.db data/csv_exports --overwrite
```

**특징:**
- 각 테이블이 `테이블명.csv` 파일로 저장
- 기본 출력 위치: DB 파일과 같은 디렉토리의 `output` 폴더

---

### 4. 단일 테이블을 CSV로 내보내기

특정 테이블만 CSV로 내보냅니다.

```bash
python script/export_db_to_csv.py <csv_file> <db_file> [-rf]
```

**예시:**
```bash
python script/export_db_to_csv.py data/Words.csv data/vocabulary.db
```

---

## Primary Key 규칙

스크립트는 다음 우선순위로 Primary Key를 자동 감지합니다:

1. **테이블에 이미 설정된 Primary Key** (최우선)
2. **테이블명Id 패턴** (예: `Words` 테이블 → `WordsId`)
3. **Id로 끝나는 가장 짧은 컬럼** (예: `word_id`, `DefId`)

### Primary Key 요구사항

- 중복 값이 없어야 함
- NULL 값이 없어야 함
- INTEGER 타입 권장

---

## Foreign Key 관계

현재 스크립트는 Foreign Key 제약을 자동으로 추가하지 않습니다. 이유:

1. **CSV 순서 의존성**: Foreign Key가 있으면 CSV 삽입 순서가 중요해짐
2. **SQLite 제한**: ALTER TABLE로 Foreign Key를 추가할 수 없음
3. **유연성**: CSV 기반 워크플로우에서는 관계를 데이터로만 관리

### 관계 확인

데이터 무결성은 별도 스크립트로 확인할 수 있습니다:

```bash
python script/analyze_db_relationships.py data/vocabulary.db
```

---

## 데이터베이스 제약 추가

기존 데이터베이스에 Primary Key를 추가할 수 있습니다:

```bash
python script/add_constraints_to_db.py <db_file> [--add-fk]
```

**예시:**
```bash
# Primary Key 추가
python script/add_constraints_to_db.py data/vocabulary.db

# Foreign Key 관계 정보 확인
python script/add_constraints_to_db.py data/vocabulary.db --add-fk
```

**주의사항:**
- Primary Key 추가 전에 중복 값과 NULL 값이 없어야 함
- Foreign Key는 정보만 출력 (실제 제약 추가는 테이블 재생성 필요)

---

## 테이블/컬럼명 변경

데이터베이스의 테이블명이나 컬럼명을 변경할 수 있습니다:

```bash
python script/rename_table_column.py <db_file> [옵션]
```

**예시:**
```bash
# 테이블명 변경
python script/rename_table_column.py data/vocabulary.db --rename-table Vocabulary Words

# 컬럼명 변경
python script/rename_table_column.py data/vocabulary.db --rename-column Words Word 단어

# 여러 컬럼명 변경
python script/rename_table_column.py data/vocabulary.db \
  --rename-column Words Word 단어 \
  --rename-column Words Meaning 의미
```

---

## 권장 워크플로우

### 초기 설정

1. CSV 파일 준비 (각 테이블별로)
2. 새 데이터베이스 생성:
   ```bash
   python script/create_db_from_csv.py data/vocabulary.db data/*.csv
   ```
3. Primary Key 확인 및 추가:
   ```bash
   python script/add_constraints_to_db.py data/vocabulary.db
   ```

### 데이터 추가/수정

1. CSV 파일 편집
2. 데이터베이스 업데이트:
   ```bash
   python script/import_csv_to_db.py data/Words.csv data/vocabulary.db -rf
   ```

### 데이터베이스 백업/복원

1. 데이터베이스를 CSV로 내보내기:
   ```bash
   python script/export_all_tables_to_csv.py data/vocabulary.db data/backup
   ```
2. 필요 시 CSV에서 다시 생성:
   ```bash
   python script/create_db_from_csv.py data/vocabulary_restored.db data/backup/*.csv
   ```

---

## 주의사항

### CSV 파일 요구사항

- **UTF-8 인코딩**: CSV 파일은 UTF-8로 저장되어야 함
- **헤더 필수**: 첫 번째 행은 컬럼명이어야 함
- **Primary Key 컬럼**: 중복 값과 NULL 값이 없어야 함

### 데이터 타입

스크립트는 다음 규칙으로 데이터 타입을 추론합니다:

- `Id`로 끝나는 컬럼 → `INTEGER`
- 숫자 값들 → `INTEGER` 또는 `REAL`
- 나머지 → `TEXT`

### 컬럼명 매핑

특수 매핑 규칙:
- `Example` → `example_sentence` (DB)
- `example_sentence` → `Example` (CSV)

---

## 문제 해결

### Primary Key 중복 오류

```bash
# 중복 값 확인
python script/analyze_db_relationships.py data/vocabulary.db
```

CSV 파일에서 중복된 Primary Key 값을 제거하거나 수정하세요.

### 컬럼명 불일치

스크립트는 자동으로 컬럼명을 매핑하지만, 필요시 수동으로 매핑 규칙을 수정할 수 있습니다:
- `script/import_csv_to_db.py`의 `get_column_mapping()` 함수
- `script/export_db_to_csv.py`의 `get_reverse_column_mapping()` 함수

---

## 관련 스크립트

| 스크립트 | 기능 |
|---------|------|
| `create_db_from_csv.py` | CSV → DB (새로 생성) |
| `import_csv_to_db.py` | CSV → DB (업데이트) |
| `export_all_tables_to_csv.py` | DB → CSV (모든 테이블) |
| `export_db_to_csv.py` | DB → CSV (단일 테이블) |
| `add_constraints_to_db.py` | Primary Key/Foreign Key 추가 |
| `rename_table_column.py` | 테이블/컬럼명 변경 |
| `review_db.py` | 데이터베이스 구조 리뷰 |
| `analyze_db_relationships.py` | 관계 및 무결성 분석 |

