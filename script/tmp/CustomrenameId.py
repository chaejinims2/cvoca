# ./CustomrenameId.py /path/file/ddd.csv Day 10 238

import csv
import sys

# 인자 확인
if len(sys.argv) != 5:
    print("사용법: python CustomrenameId.py <input_file> <column_name> <condition_value> <add_value>")
    print("예시: python CustomrenameId.py input.csv Day 10 238")
    sys.exit(1)

input_file = sys.argv[1]
column_name = sys.argv[2]
condition_value = sys.argv[3]
add_value = int(sys.argv[4])

output_file = input_file

# CSV 파일 읽기
rows = []
updated_count = 0

with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    
    # 컬럼 존재 확인
    if column_name not in fieldnames:
        print(f"오류: 컬럼 '{column_name}'가 파일에 존재하지 않습니다.")
        print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
        sys.exit(1)
    
    if 'Id' not in fieldnames:
        print(f"오류: 'Id' 컬럼이 파일에 존재하지 않습니다.")
        sys.exit(1)
    
    for row in reader:
        # 조건 확인: 지정한 컬럼의 값이 condition_value와 일치하는지
        if str(row[column_name]).strip() == str(condition_value).strip():
            # Id에 add_value 더하기
            try:
                current_id = int(row['Id'])
                row['Id'] = str(current_id + add_value)
                updated_count += 1
            except ValueError:
                print(f"경고: Id 값 '{row['Id']}'를 숫자로 변환할 수 없습니다. 건너뜁니다.")
        rows.append(row)

# 파일에 저장
with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"처리 완료: {column_name} == {condition_value}인 {updated_count}개 행의 Id에 {add_value}를 더했습니다.")
print(f"결과가 {output_file}에 저장되었습니다.")

