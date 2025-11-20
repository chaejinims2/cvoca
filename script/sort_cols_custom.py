# ./sort_columns_custom.py /path/to/input.csv Id Word Day

import csv
import sys
import os

# 인자 확인
if len(sys.argv) < 2:
    print("사용법: python sort_columns_custom.py <input_file> <column1> <column2> ...")
    print("예시: python sort_columns_custom.py input.csv Id Word Day")
    sys.exit(1)

input_file = sys.argv[1]

# 입력 파일의 디렉토리에 output 폴더 생성
input_dir = os.path.dirname(os.path.abspath(input_file))
output_dir = os.path.join(input_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

base_name = os.path.basename(os.path.splitext(input_file)[0])
ext = os.path.splitext(input_file)[1]
output_file = os.path.join(output_dir, f"{base_name}_sorted{ext}")

# 파일 첫 번째 행 읽어서 컬럼 수 확인
with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    first_row = next(reader)
    column_count = len(first_row)
    
    # 인자 개수 확인 (파일명 + 컬럼들)
    if len(sys.argv) < column_count + 1:
        print(f"오류: 컬럼 인자 수는 {column_count}개여야 합니다.")
        print(f"현재 파일의 컬럼: {', '.join(first_row)}")
        print(f"사용법: python sort_columns_custom.py {input_file} {' '.join(first_row)}")
        sys.exit(1)

# 인자로 받은 컬럼 순서
desired_order = sys.argv[2:]

# CSV 파일 읽기
rows = []
with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    original_fieldnames = reader.fieldnames
    
    # 원본 컬럼이 모두 존재하는지 확인
    for col in desired_order:
        if col not in original_fieldnames:
            print(f"오류: 컬럼 '{col}'가 파일에 존재하지 않습니다.")
            print(f"사용 가능한 컬럼: {', '.join(original_fieldnames)}")
            sys.exit(1)
    
    for row in reader:
        rows.append(row)

# 지정한 컬럼 순서대로 파일 저장
with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=desired_order)
    writer.writeheader()
    
    for row in rows:
        # 지정한 순서대로 딕셔너리 재구성
        new_row = {}
        for col in desired_order:
            new_row[col] = row[col]
        writer.writerow(new_row)

print(f"처리 완료: {input_file}의 컬럼을 지정한 순서로 재배열하여 {output_file}에 저장되었습니다.")
print(f"새로운 컬럼 순서: {', '.join(desired_order)}")
