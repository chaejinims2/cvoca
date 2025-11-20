#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
세 CSV 파일(Vocabulary, Meaning, Example) 간의 매핑을 검증하는 스크립트
사용법: python script/validate_mapping.py <vocabulary.csv> <meaning.csv> <example.csv> [output_file]
"""

import csv
import sys
import os

def validate_mapping(vocabulary_file, meaning_file, example_file, output_file=None):
    """
    세 CSV 파일 간의 매핑을 검증
    
    Args:
        vocabulary_file: Vocabulary.csv 파일 경로
        meaning_file: Meaning.csv 파일 경로
        example_file: Example.csv 파일 경로
        output_file: 검증 결과를 저장할 파일 경로 (None이면 출력만)
    """
    errors = []
    warnings = []
    
    # 파일 존재 확인
    for file_path in [vocabulary_file, meaning_file, example_file]:
        if not os.path.exists(file_path):
            print(f"오류: 파일 '{file_path}'을 찾을 수 없습니다.")
            sys.exit(1)
    
    # Vocabulary 파일 읽기
    vocabulary_word_ids = set()
    vocabulary_data = {}
    
    with open(vocabulary_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word_id = row.get('word_id', '').strip()
            if word_id:
                vocabulary_word_ids.add(word_id)
                vocabulary_data[word_id] = row
    
    print(f"Vocabulary: {len(vocabulary_word_ids)}개 항목 로드")
    
    # Meaning 파일 읽기
    meaning_ids = set()
    meaning_data = {}
    invalid_word_refs = []
    invalid_mean_id_calc = []
    
    with open(meaning_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):  # 헤더 다음부터 시작
            mean_id = row.get('sense_no', '').strip()
            word_id = row.get('word_id', '').strip()
            def_id = row.get('DefId', '').strip()
            
            if mean_id:
                meaning_ids.add(mean_id)
                meaning_data[mean_id] = row
            
            # word_id가 Vocabulary에 존재하는지 확인
            if word_id and word_id not in vocabulary_word_ids:
                invalid_word_refs.append({
                    'row': idx,
                    'mean_id': mean_id,
                    'word_id': word_id,
                    'word': vocabulary_data.get(word_id, {}).get('Word', 'N/A')
                })
                errors.append(f"Meaning 행 {idx}: word_id {word_id}가 Vocabulary에 존재하지 않습니다.")
            
            # sense_no 계산 검증: sense_no = word_id * 10 + DefId
            if mean_id and word_id and def_id:
                try:
                    expected_mean_id = int(word_id) * 10 + int(def_id)
                    actual_mean_id = int(mean_id)
                    if actual_mean_id != expected_mean_id:
                        invalid_mean_id_calc.append({
                            'row': idx,
                            'mean_id': mean_id,
                            'word_id': word_id,
                            'def_id': def_id,
                            'expected': expected_mean_id,
                            'actual': actual_mean_id
                        })
                        errors.append(f"Meaning 행 {idx}: sense_no 계산 오류 - word_id {word_id} * 10 + DefId {def_id} = {expected_mean_id}, 실제 sense_no = {actual_mean_id}")
                except ValueError:
                    pass  # 숫자가 아닌 경우는 스킵
    
    print(f"Meaning: {len(meaning_ids)}개 항목 로드")
    if invalid_word_refs:
        print(f"  경고: {len(invalid_word_refs)}개의 잘못된 word_id 참조 발견")
    if invalid_mean_id_calc:
        print(f"  경고: {len(invalid_mean_id_calc)}개의 sense_no 계산 오류 발견")
    
    # Example 파일 읽기
    example_ids = set()
    example_data = {}
    invalid_meaning_refs = []
    invalid_exam_id_calc = []
    
    with open(example_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):  # 헤더 다음부터 시작
            exam_id = row.get('ExamId', '').strip()
            mean_id = row.get('sense_no', '').strip()
            use_id = row.get('example_no', '').strip()
            
            if exam_id:
                example_ids.add(exam_id)
                example_data[exam_id] = row
            
            # MeanId가 Meaning에 존재하는지 확인
            if mean_id and mean_id not in meaning_ids:
                invalid_meaning_refs.append({
                    'row': idx,
                    'exam_id': exam_id,
                    'mean_id': mean_id
                })
                errors.append(f"Example 행 {idx}: sense_no {mean_id}가 Meaning에 존재하지 않습니다.")
            
            # ExamId 계산 검증: ExamId = sense_no * 10 + example_no
            if exam_id and mean_id and use_id:
                try:
                    expected_exam_id = int(mean_id) * 10 + int(use_id)
                    actual_exam_id = int(exam_id)
                    if actual_exam_id != expected_exam_id:
                        invalid_exam_id_calc.append({
                            'row': idx,
                            'exam_id': exam_id,
                            'mean_id': mean_id,
                            'use_id': use_id,
                            'expected': expected_exam_id,
                            'actual': actual_exam_id
                        })
                        errors.append(f"Example 행 {idx}: ExamId 계산 오류 - sense_no {mean_id} * 10 + example_no {use_id} = {expected_exam_id}, 실제 ExamId = {actual_exam_id}")
                except ValueError:
                    pass  # 숫자가 아닌 경우는 스킵
    
    print(f"Example: {len(example_ids)}개 항목 로드")
    if invalid_meaning_refs:
        print(f"  경고: {len(invalid_meaning_refs)}개의 잘못된 sense_no 참조 발견")
    if invalid_exam_id_calc:
        print(f"  경고: {len(invalid_exam_id_calc)}개의 ExamId 계산 오류 발견")
    
    # Vocabulary에 연결되지 않은 Meaning 찾기
    orphaned_meanings = []
    for meaning_id, meaning_row in meaning_data.items():
        word_id = meaning_row.get('word_id', '').strip()
        if not word_id or word_id not in vocabulary_word_ids:
            orphaned_meanings.append({
                'meaning_id': meaning_id,
                'word_id': word_id,
                'meaning': meaning_row.get('Meaning', 'N/A')
            })
    
    # Meaning에 연결되지 않은 Example 찾기
    orphaned_examples = []
    for exam_id, example_row in example_data.items():
        mean_id = example_row.get('sense_no', '').strip()
        if not mean_id or mean_id not in meaning_ids:
            orphaned_examples.append({
                'exam_id': exam_id,
                'mean_id': mean_id,
                'usage': example_row.get('Usage', 'N/A')[:50]  # 처음 50자만
            })
    
    # Vocabulary에 연결된 Meaning이 없는 경우 찾기
    vocab_without_meanings = []
    for word_id in vocabulary_word_ids:
        # Meaning에서 이 word_id를 참조하는 항목이 있는지 확인
        has_meaning = any(
            m.get('word_id', '').strip() == word_id 
            for m in meaning_data.values()
        )
        if not has_meaning:
            vocab_without_meanings.append({
                'word_id': word_id,
                'word': vocabulary_data.get(word_id, {}).get('Word', 'N/A')
            })
            warnings.append(f"Vocabulary word_id {word_id} ({vocabulary_data.get(word_id, {}).get('Word', 'N/A')})에 연결된 Meaning이 없습니다.")
    
    # Meaning에 연결된 Example이 없는 경우 찾기
    meaning_without_examples = []
    for mean_id in meaning_ids:
        # Example에서 이 MeanId를 참조하는 항목이 있는지 확인
        has_example = any(
            e.get('sense_no', '').strip() == mean_id 
            for e in example_data.values()
        )
        if not has_example:
            meaning_without_examples.append({
                'mean_id': mean_id,
                'word_id': meaning_data.get(mean_id, {}).get('word_id', 'N/A'),
                'meaning': meaning_data.get(mean_id, {}).get('Meaning', 'N/A')[:50]
            })
            warnings.append(f"Meaning sense_no {mean_id}에 연결된 Example이 없습니다.")
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"검증 결과 요약")
    print(f"{'='*60}")
    print(f"오류: {len(errors)}개")
    print(f"경고: {len(warnings)}개")
    
    if errors:
        print(f"\n오류 목록:")
        for i, error in enumerate(errors[:20], 1):  # 최대 20개만 출력
            print(f"  {i}. {error}")
        if len(errors) > 20:
            print(f"  ... 외 {len(errors) - 20}개")
    
    if warnings:
        print(f"\n경고 목록:")
        for i, warning in enumerate(warnings[:20], 1):  # 최대 20개만 출력
            print(f"  {i}. {warning}")
        if len(warnings) > 20:
            print(f"  ... 외 {len(warnings) - 20}개")
    
    # 상세 통계
    print(f"\n상세 통계:")
    print(f"  Vocabulary 항목: {len(vocabulary_word_ids)}개")
    print(f"  Meaning 항목: {len(meaning_ids)}개")
    print(f"  Example 항목: {len(example_ids)}개")
    print(f"  잘못된 word_id 참조: {len(invalid_word_refs)}개")
    print(f"  잘못된 sense_no 참조: {len(invalid_meaning_refs)}개")
    print(f"  sense_no 계산 오류: {len(invalid_mean_id_calc)}개")
    print(f"  ExamId 계산 오류: {len(invalid_exam_id_calc)}개")
    print(f"  고아 Meaning (Vocabulary 없음): {len(orphaned_meanings)}개")
    print(f"  고아 Example (Meaning 없음): {len(orphaned_examples)}개")
    print(f"  Meaning 없는 Vocabulary: {len(vocab_without_meanings)}개")
    print(f"  Example 없는 Meaning: {len(meaning_without_examples)}개")
    
    # 결과를 파일로 저장
    if output_file:
        # 입력 파일의 디렉토리에 output 폴더 생성
        input_dir = os.path.dirname(os.path.abspath(vocabulary_file))
        output_dir = os.path.join(input_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # output_file이 상대 경로면 output 폴더에 저장
        if not os.path.isabs(output_file):
            output_file = os.path.join(output_dir, os.path.basename(output_file))
        
        with open(output_file, 'w', encoding='utf-8', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(['구분', '유형', 'ID', '참조 ID', '상세 정보'])
            
            # 오류 기록
            for error in errors:
                writer.writerow(['오류', '매핑 오류', '', '', error])
            
            # 경고 기록
            for warning in warnings:
                writer.writerow(['경고', '연결 없음', '', '', warning])
            
            # 잘못된 참조
            for ref in invalid_word_refs:
                writer.writerow(['오류', '잘못된 word_id', ref['mean_id'], ref['word_id'], 
                               f"Meaning 행 {ref['row']}: word_id {ref['word_id']}가 존재하지 않음"])
            
            for ref in invalid_meaning_refs:
                writer.writerow(['오류', '잘못된 sense_no', ref['exam_id'], ref['mean_id'],
                               f"Example 행 {ref['row']}: sense_no {ref['mean_id']}가 존재하지 않음"])
            
            # 계산 오류
            for calc in invalid_mean_id_calc:
                writer.writerow(['오류', 'sense_no 계산 오류', calc['mean_id'], calc['word_id'],
                               f"Meaning 행 {calc['row']}: word_id {calc['word_id']} * 10 + DefId {calc['def_id']} = {calc['expected']}, 실제 = {calc['actual']}"])
            
            for calc in invalid_exam_id_calc:
                writer.writerow(['오류', 'ExamId 계산 오류', calc['exam_id'], calc['mean_id'],
                               f"Example 행 {calc['row']}: sense_no {calc['mean_id']} * 10 + example_no {calc['use_id']} = {calc['expected']}, 실제 = {calc['actual']}"])
            
            # 고아 레코드
            for orphan in orphaned_meanings:
                writer.writerow(['경고', '고아 Meaning', orphan['meaning_id'], orphan['word_id'],
                               f"Meaning: {orphan['meaning']}"])
            
            for orphan in orphaned_examples:
                writer.writerow(['경고', '고아 Example', orphan['exam_id'], orphan['mean_id'],
                               f"Usage: {orphan['usage']}"])
            
            # 연결 없는 레코드
            for vocab in vocab_without_meanings:
                writer.writerow(['경고', 'Meaning 없는 Vocabulary', vocab['word_id'], '',
                               f"Word: {vocab['word']}"])
            
            for meaning in meaning_without_examples:
                writer.writerow(['경고', 'Example 없는 Meaning', meaning['mean_id'], meaning['word_id'],
                               f"Meaning: {meaning['meaning']}"])
        
        print(f"\n결과가 '{output_file}'에 저장되었습니다.")
    
    # 종료 코드
    if errors:
        print(f"\n검증 실패: {len(errors)}개의 오류가 발견되었습니다.")
        sys.exit(1)
    elif warnings:
        print(f"\n검증 완료: {len(warnings)}개의 경고가 있습니다.")
        sys.exit(0)
    else:
        print(f"\n검증 성공: 모든 매핑이 올바릅니다!")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("사용법: python script/validate_mapping.py <vocabulary.csv> <meaning.csv> <example.csv> [output_file]")
        print("예시: python script/validate_mapping.py Vocabulary.csv Meaning.csv Example.csv")
        print("      python script/validate_mapping.py Vocabulary.csv Meaning.csv Example.csv validation_result.csv")
        sys.exit(1)
    
    vocabulary_file = sys.argv[1]
    meaning_file = sys.argv[2]
    example_file = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None
    
    validate_mapping(vocabulary_file, meaning_file, example_file, output_file)

