## 데이터베이스 초기 생성 (최초 1회)

### 1. 기본 설정값

단어책 기본 정보 기반으로 새로운 데이터베이스에 대한 정보를 설정합니다.

```bash
python script/init_book_db.py <BASEBOOK_NAME> <MAX_DAYS_NUM> <MAX_WORD_NUM>
```

**예시:**
```bash
# ielts_voca라는 이름으로 Day 20, 각 Day 별 단어수 30개로 기본 데이터베이스(.db)와 새로운 테이블들(.csv) 생성
python script/1117/init_book_db.py ielts_voca 20 30
```
**산출물:**
- baseDB: 기본 데이터베이스 (path: data/ielts_voca_20_30.db)
- baseWords: 단일 테이블 csv, (data/ielts_voca_20_30/Words.csv (readonly))
- baseDefinitions: 단일 테이블 csv, (data/ielts_voca_20_30/Definitions.csv (readonly))
- baseExamples: 단일 테이블 csv, (data/ielts_voca_20_30/Examples.csv (readonly))
- myWords: 복사된 작업 가능한 테이블 (data/ielts_voca_20_30/user/Words.csv)
- myDefinitions:복사된 작업 가능한 테이블, (data/ielts_voca_20_30/user/Definitions.csv)
- myExamples:복사된 작업 가능한 테이블 (data/ielts_voca_20_30/user/Examples.csv)

**특징:**
- 학습 시 수정 가능한 파일은 user 폴더 내부의 폴더만 가능.
- 한번 정해진 파일경로는 바뀌지 않으며, 설명상 편의를 위하여 별칭으로 표기 (예: baseDB, baseWords...)
- 다음 상수를 계속 사용함 : MAX_VOCA_BY_DAY = MAX_DAYS_NUM, MAX_SENSES_PER_WORD = 10, MAX_EXAMPLES_PER_SENSES = 10



### 2. 테이블 구조
기본 데이터베이스 파일명 형식: {BASEBOOK_NAME}_{MAX_DAYS_NUM}_{MAX_WORD_NUM}.db
예시: ielts_voca_20_30.db

테이블 체인: Words -> Definitions -> Examples

[Words 테이블]
- day_no: Foreign Key (일차 번호, 1부터 MAX_DAYS_NUM까지)
- word_no: 로컬 키 (하루 내 단어 번호, 1부터 MAX_WORD_NUM까지)
- word_id: Primary Key (단어 고유 ID)
- Word: 단어 텍스트

[Definitions 테이블]
- word_id: Foreign Key (Words 테이블 참조)
- sense_no: 로컬 키 (의미 번호, 0부터 시작 MAX_SENSES_PER_WORD-1까지)
- definition_id: Primary Key (정의 고유 ID)
- definition: 정의 텍스트
- part_of_speech: 품사

[Examples 테이블]
- definition_id: Foreign Key (Definitions 테이블 참조)
- example_no: 로컬 키 (용도 번호, 0부터 시작 MAX_EXAMPLES_PER_SENSES-1까지)
- example_id: Primary Key (예문 고유 ID)
- example_sentence: 예문 텍스트

### 3. ID 생성 규칙 (연산식)
Words 테이블: word_id = day_no * MAX_WORD_NUM + word_no
예시: day_no=1, word_no=1 -> word_id = 1 * 30 + 1 = 31
예시: day_no=1, word_no=30 -> word_id = 1 * 30 + 30 = 60
예시: day_no=2, word_no=1 -> word_id = 2 * 30 + 1 = 61

Definitions 테이블: definition_id = word_id * 10 + sense_no
예시: word_id=1, sense_no=0 -> definition_id = 1 * 10 + 0 = 10
예시: word_id=1, sense_no=1 -> definition_id = 1 * 10 + 1 = 11

Examples 테이블: example_id = definition_id * 10 + example_no
예시: definition_id=10, example_no=0 -> example_id = 10 * 10 + 0 = 100
예시: definition_id=10, example_no=1 -> example_id = 10 * 10 + 1 = 101


day_no=7, word_no=25, sense_no=1, example_no=1

 definition_id = 1 * 10 + 0 = 10

### 4. 초기 데이터 생성 규칙
최초 데이터베이스 생성 시 모든 테이블에 기본 행이 생성됨.

Words 테이블: MAX_DAYS_NUM * MAX_WORD_NUM 개의 행 생성
- 각 행의 Word 컬럼에는 "TempWord_{word_id}" 형식의 임시 값이 들어감
- 예시: word_id=1 -> Word="TempWord_1"

Definitions 테이블: MAX_DAYS_NUM * MAX_WORD_NUM 개의 행 생성 (최소)
- 각 행의 definition 컬럼에는 "TempDefinition_{definition_id}" 형식의 임시 값이 들어감
- part_of_speech 컬럼에는 null이 들어감
- 예시: definition_id=10 -> definition="TempDefinition_10", part_of_speech=null

Examples 테이블: MAX_DAYS_NUM * MAX_WORD_NUM 개의 행 생성 (최소)
- 각 행의 example_sentence 컬럼에는 "TempExample_{example_id}" 형식의 임시 값이 들어감
- 예시: example_id=100 -> example_sentence="TempExample_100"

## 데이터베이스 데이터 수정 워크플로우

### 전제 조건
- 1회독 상태를 가정 (기존 데이터가 최초 생성 데이터 상태)
- Words, Definitions, Examples 테이블에 데이터를 순차적으로 수정해야 함
- TempWord, TempDefinition, TempExample가 포함된 행은 유효하지 않은 데이터로 간주

### 1. Words 테이블 수정
- 테이블 크기: 고정 (MAX_DAYS_NUM * MAX_WORD_NUM)
- 단어 추가 불가, 기존 행만 수정 가능
- Word 컬럼의 "TempWord_{word_id}" 값을 실제 단어로 수정
- 예시: word_id=1의 "TempWord_1" -> "avert"로 수정

### 2. Definitions 테이블 수정
- 테이블 크기: 가변 가능 (최소 MAX_DAYS_NUM * MAX_WORD_NUM)
- 최초 생성 시 생성된 행은 삭제 불가 (줄어들 수 없음)
- 다의어를 고려한 기능 (하나의 단어에 여러 의미 가능)
*/+94

기존 행 수정:
- definition 컬럼의 "TempDefinition_{definition_id}" 값을 실제 정의로 수정
- part_of_speech 컬럼의 null 값을 실제 품사로 수정
- 예시: definition_id=10의 "TempDefinition_10" -> "피하다, 막다", part_of_speech=null -> "v"로 수정

새로운 의미 추가 (다의어):
- 동일한 word_id를 가진 행들 중 MeanId가 가장 큰 값을 찾음
- 새로운 sense_no = 기존 최대 sense_no + 1
- 새로운 definition_id = word_id * 10 + 새로운 MeanId로 계산
- 새로운 행을 생성하고 definition="TempDefinition_{새로운DefinitionId}", part_of_speech=null로 설정
- 사용자가 해당 행을 수정하여 실제 정의와 품사를 입력
- 이때 Examples 테이블에도 자동으로 해당 DefinitionId에 매핑되는 새로운 기본 행이 생성됨
- 예시: word_id=3에 이미 sense_no=0 (definition_id=30)이 있는 경우, sense_no=1 (definition_id=31) 행을 새로 생성

### 3. Examples 테이블 수정
- 테이블 크기: 가변 가능 (최소 MAX_DAYS_NUM * MAX_WORD_NUM)
- 최초 생성 시 생성된 행은 삭제 불가 (줄어들 수 없음)
- 하나의 정의에 여러 예문을 추가할 수 있는 기능

기존 행 수정:
- example_sentence 컬럼의 "TempExample_{example_id}" 값을 실제 예문으로 수정
- 예시: example_id=100의 "TempExample_100" -> "He averted financial disaster..."로 수정

새로운 예문 추가:
- 동일한 DefinitionId를 가진 행들 중 UseId가 가장 큰 값을 찾음
- 새로운 example_no = 기존 최대 example_no + 1
- 새로운 example_id = definition_id * 10 + 새로운 UseId로 계산
- 새로운 행을 생성하고 example_sentence="TempExample_{새로운ExampleId}"로 설정
- 사용자가 해당 행을 수정하여 실제 예문을 입력
- 예시: definition_id=10에 이미 example_no=0 (example_id=100)이 있는 경우, example_no=1 (example_id=101) 행을 새로 생성

## 데이터 무결성 규칙
- TempWord가 포함된 Word는 유효하지 않은 단어로 간주
- TempDefinition이 포함된 Definition은 유효하지 않은 정의로 간주
- TempExample가 포함된 ExampleSentence는 유효하지 않은 예문으로 간주
- Words -> Definitions -> Examples 체인이 완전해야 유효한 데이터로 간주
