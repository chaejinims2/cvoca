#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 파일의 definition 컬럼에서 PartOfSpeech를 분리하는 스크립트
사용법: python script/split_definition.py <input_file> [output_file]
"""

import csv
import sys
import os
import re

def parse_definition(definition):
    """
    definition 문자열에서 PartOfSpeech와 Definition을 분리
    
    Args:
        definition: "v. 조화시키다" 형식의 문자열
        
    Returns:
        (part_of_speech, definition) 튜플
        예: ("v", "조화시키다")
    """
    if not definition or not definition.strip():
        return None, None
    
    definition = definition.strip()
    
    # 품사 패턴: v., n., a., ad., prep., conj. 등
    # 패턴: 알파벳(소문자) + 점 + 공백
    pattern = r'^([a-z]+)\.\s+(.+)$'
    match = re.match(pattern, definition, re.IGNORECASE)
    
    if match:
        part_of_speech = match.group(1).lower()  # 소문자로 정규화
        definition_text = match.group(2).strip()
        return part_of_speech, definition_text
    else:
        # 패턴이 맞지 않으면 전체를 Definition으로, PartOfSpeech는 None
        return None, definition

def split_definition_column(input_file, output_file=None):
    """
    CSV 파일의 definition 컬럼을 PartOfSpeech와 Definition으로 분리
    
    Args:
        input_file: 입력 CSV 파일 경로
        output_file: 출력 CSV 파일 경로 (None이면 입력 파일명에 _split 추가)
    """
    if not os.path.exists(input_file):
        print(f"오류: 파일 '{input_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        ext = os.path.splitext(input_file)[1]
        output_file = f"{base_name}_split{ext}"
    
    rows = []
    processed_count = 0
    error_count = 0
    
    # CSV 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # definition 컬럼이 있는지 확인
        if 'definition' not in fieldnames:
            print(f"오류: CSV 파일에 'definition' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(fieldnames)}")
            sys.exit(1)
        
        # part_of_speech 컬럼이 이미 있으면 경고
        if 'part_of_speech' in fieldnames:
            print("경고: 'part_of_speech' 컬럼이 이미 존재합니다. 기존 컬럼을 덮어씁니다.")
            # definition 다음에 part_of_speech 삽입
            def_index = fieldnames.index('definition')
            if 'part_of_speech' in fieldnames:
                fieldnames.remove('part_of_speech')
            fieldnames.insert(def_index + 1, 'part_of_speech')
        else:
            # definition 다음에 part_of_speech 삽입
            def_index = fieldnames.index('definition')
            fieldnames.insert(def_index + 1, 'part_of_speech')
        
        for row in reader:
            definition = row.get('definition', '').strip()
            
            if not definition:
                # Definition이 비어있으면 그대로 유지
                row['part_of_speech'] = ''
                rows.append(row)
                continue
            
            # definition 파싱
            part_of_speech, definition_text = parse_definition(definition)
            
            if part_of_speech:
                row['part_of_speech'] = part_of_speech
                row['definition'] = definition_text
                processed_count += 1
            else:
                # 파싱 실패 시 PartOfSpeech는 빈 문자열
                row['part_of_speech'] = ''
                if definition_text:
                    row['definition'] = definition_text
                error_count += 1
                print(f"경고: 파싱 실패 - '{definition}'")
            
            rows.append(row)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"처리 완료!")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    print(f"  총 행 수: {len(rows)}개")
    print(f"  성공적으로 파싱된 행: {processed_count}개")
    if error_count > 0:
        print(f"  파싱 실패한 행: {error_count}개")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python script/split_definition.py <input_file> [output_file]")
        print("예시: python script/split_definition.py alll.csv alll_split.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    split_definition_column(input_file, output_file)

