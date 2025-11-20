#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
두 CSV 파일을 조인하는 스크립트 (중간 테이블을 통한 간접 조인 지원)
사용법: python script/join_csv.py <left_file.csv> <right_file.csv> <left_key> <right_key> [middle_file.csv] [join_type] [output_file]
"""

import csv
import sys
import os

def find_indirect_path(left_file, right_file, left_key, right_key):
    """
    중간 테이블을 통한 간접 조인 경로 찾기
    data 폴더의 모든 CSV 파일을 탐색하여 두 키를 모두 가진 중간 파일을 찾음
    
    Returns:
        (middle_file, left_to_middle_key, middle_id, middle_to_right_key) 또는 None
    """
    # 왼쪽/오른쪽 파일의 디렉토리 찾기 (보통 data 폴더)
    left_dir = os.path.dirname(os.path.abspath(left_file))
    right_dir = os.path.dirname(os.path.abspath(right_file))
    
    # 공통 디렉토리 찾기 (보통 둘 다 같은 data 폴더에 있음)
    search_dir = left_dir if left_dir == right_dir else left_dir
    
    # 왼쪽/오른쪽 파일명에서 테이블명 추출
    left_table_name = os.path.splitext(os.path.basename(left_file))[0]
    right_table_name = os.path.splitext(os.path.basename(right_file))[0]
    
    # 왼쪽/오른쪽 파일의 전체 경로 (제외할 파일)
    left_abs = os.path.abspath(left_file)
    right_abs = os.path.abspath(right_file)
    
    # search_dir의 모든 CSV 파일 탐색 (output 하위 제외)
    if not os.path.exists(search_dir):
        return None
    
    # CSV 파일 목록 수집
    csv_files = []
    for root, dirs, files in os.walk(search_dir):
        # output 하위 디렉토리 제외
        if 'output' in root.split(os.sep):
            continue
        
        for file in files:
            if file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                # 왼쪽/오른쪽 파일 자체는 제외
                abs_path = os.path.abspath(file_path)
                if abs_path == left_abs or abs_path == right_abs:
                    continue
                csv_files.append(file_path)
    
    # 각 CSV 파일을 중간 테이블 후보로 검사
    for middle_file in csv_files:
        try:
            with open(middle_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                middle_columns = list(reader.fieldnames)
                
                if not middle_columns:
                    continue
                
                # 중간 테이블의 Id 컬럼 찾기
                middle_id = None
                for col in middle_columns:
                    if col.lower() == 'id':
                        middle_id = col
                        break
                
                if not middle_id:
                    continue
                
                # 왼쪽 테이블을 참조하는 컬럼 찾기
                # 예: aaa.csv (Id) -> 중간파일 (aaaId)
                left_to_middle = None
                
                # 패턴 1: {left_table_name}Id (예: VocabularyId)
                left_id_pattern = f"{left_table_name}Id"
                for col in middle_columns:
                    if col == left_id_pattern or col.lower() == left_id_pattern.lower():
                        left_to_middle = col
                        break
                
                # 패턴 2: left_key를 포함하는 컬럼 (예: Id -> VocabularyId)
                if not left_to_middle:
                    for col in middle_columns:
                        if left_key.lower() in col.lower() or col.lower() in left_key.lower():
                            if 'id' in col.lower() and col != middle_id:
                                # left_table_name과 관련이 있는지 확인
                                if left_table_name.lower() in col.lower():
                                    left_to_middle = col
                                    break
                
                # 오른쪽 테이블을 참조하는 컬럼 찾기
                # 예: ccc.csv (Id) -> 중간파일 (cccId)
                middle_to_right = None
                
                # 패턴 1: {right_table_name}Id (예: example_id)
                right_id_pattern = f"{right_table_name}Id"
                for col in middle_columns:
                    if col == right_id_pattern or col.lower() == right_id_pattern.lower():
                        middle_to_right = col
                        break
                
                # 패턴 2: right_key를 포함하는 컬럼 (예: MeaningId)
                if not middle_to_right:
                    for col in middle_columns:
                        if right_key.lower() in col.lower() or col.lower() in right_key.lower():
                            if 'id' in col.lower() and col != middle_id:
                                # right_table_name과 관련이 있는지 확인
                                if right_table_name.lower() in col.lower():
                                    middle_to_right = col
                                    break
                
                # 패턴 3: right_key가 중간 테이블의 Id를 직접 참조하는 경우
                # 예: Example.MeaningId -> Meaning.Id
                if not middle_to_right:
                    # right_key가 "MeaningId" 같은 형태면 middle_id를 사용
                    if right_key.lower().endswith('id') and right_key.lower() != 'id':
                        # right_key에서 테이블명 추출 (예: MeaningId -> Meaning)
                        key_table = right_key[:-2] if right_key.endswith('Id') else right_key[:-2].lower()
                        middle_table_name = os.path.splitext(os.path.basename(middle_file))[0]
                        if key_table.lower() == middle_table_name.lower():
                            middle_to_right = middle_id
                
                # 경로가 완성되었는지 확인
                if left_to_middle and middle_id:
                    # 오른쪽 파일에서 right_key가 있는지 확인
                    with open(right_file, 'r', encoding='utf-8') as rf:
                        r_reader = csv.DictReader(rf)
                        r_columns = list(r_reader.fieldnames)
                        if right_key in r_columns:
                            # middle_to_right가 명시되지 않았으면 middle_id 사용
                            if not middle_to_right:
                                middle_to_right = middle_id
                            return (middle_file, left_to_middle, middle_id, middle_to_right)
        except Exception as e:
            # 파일 읽기 오류 시 다음 파일로
            continue
    
    return None

def join_csv_files(left_file, right_file, left_key, right_key, middle_file=None, join_type='inner', output_file=None):
    """
    두 CSV 파일을 조인
    
    Args:
        left_file: 왼쪽 CSV 파일 경로
        right_file: 오른쪽 CSV 파일 경로
        left_key: 왼쪽 파일의 키 컬럼명
        right_key: 오른쪽 파일의 키 컬럼명
        join_type: 조인 타입 ('inner', 'left', 'right', 'full')
        output_file: 출력 CSV 파일 경로 (None이면 자동 생성)
    """
    if not os.path.exists(left_file):
        print(f"오류: 파일 '{left_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if not os.path.exists(right_file):
        print(f"오류: 파일 '{right_file}'을 찾을 수 없습니다.")
        sys.exit(1)
    
    if join_type not in ['inner', 'left', 'right', 'full']:
        print(f"오류: 잘못된 조인 타입 '{join_type}'입니다.")
        print("      사용 가능한 타입: inner, left, right, full")
        sys.exit(1)
    
    # 직접 조인 가능한지 확인
    with open(left_file, 'r', encoding='utf-8') as f:
        left_reader = csv.DictReader(f)
        left_columns = list(left_reader.fieldnames)
    
    with open(right_file, 'r', encoding='utf-8') as f:
        right_reader = csv.DictReader(f)
        right_columns = list(right_reader.fieldnames)
    
    # 직접 조인 가능한지 확인
    use_indirect = False
    can_direct_join = (right_key in right_columns and left_key in left_columns)
    
    # 직접 조인 가능하더라도, left_key와 right_key가 서로 다른 테이블을 참조하는 경우 간접 조인 시도
    # 예: Vocabulary.Id와 Example.MeaningId는 직접 연결되지 않음
    # 단, 이미 조인된 파일(예: Vocabulary_left_join_Meaning.csv)의 경우 직접 조인 가능
    needs_indirect = False
    if can_direct_join:
        # left_key가 right_file에 있는지, right_key가 left_file에 있는지 확인
        # 둘 다 없으면 간접 조인이 필요
        left_has_right_key = right_key in left_columns
        right_has_left_key = left_key in right_columns
        
        # 이미 조인된 파일인지 확인 (예: _join_ 또는 _right 같은 접미사가 있는 경우)
        # 또는 left_key가 _right, _middle 같은 접미사를 가지고 있는 경우 직접 조인 가능
        is_already_joined = (
            '_join_' in os.path.basename(left_file).lower() or
            '_right' in left_key.lower() or
            '_middle' in left_key.lower() or
            left_key.endswith('_right') or
            left_key.endswith('_middle')
        )
        
        if not left_has_right_key and not right_has_left_key and not is_already_joined:
            # 서로 다른 테이블을 참조하므로 간접 조인 필요
            needs_indirect = True
            print(f"정보: '{left_key}'와 '{right_key}'가 서로 다른 테이블을 참조합니다.")
            print(f"      중간 테이블을 통한 간접 조인을 시도합니다...")
    
    # 직접 조인 불가능하거나 간접 조인이 필요한 경우
    if not can_direct_join or needs_indirect or middle_file:
        if not can_direct_join:
            print(f"경고: 직접 조인이 불가능합니다.")
            print(f"      '{right_file}'에 '{right_key}' 컬럼이 없거나, '{left_file}'에 '{left_key}' 컬럼이 없습니다.")
        
        if middle_file is None:
            if not needs_indirect:
                print("      중간 테이블을 통한 간접 조인을 시도합니다...")
            indirect_path = find_indirect_path(left_file, right_file, left_key, right_key)
            if indirect_path:
                middle_file, left_to_middle, middle_id, middle_to_right = indirect_path
                use_indirect = True
                print(f"      중간 테이블 발견: {os.path.basename(middle_file)}")
                print(f"      조인 경로: {left_key} -> {left_to_middle} -> {middle_id} -> {middle_to_right}")
            else:
                print(f"오류: 간접 조인 경로를 찾을 수 없습니다.")
                sys.exit(1)
        else:
            # 중간 파일이 명시적으로 지정됨
            use_indirect = True
            print(f"      중간 테이블 사용: {os.path.basename(middle_file)}")
    
    if output_file is None:
        # 입력 파일의 디렉토리에 output 폴더 생성
        input_dir = os.path.dirname(os.path.abspath(left_file))
        output_dir = os.path.join(input_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        left_base = os.path.basename(os.path.splitext(left_file)[0])
        right_base = os.path.basename(os.path.splitext(right_file)[0])
        ext = os.path.splitext(left_file)[1]
        output_file = os.path.join(output_dir, f"{left_base}_{join_type}_join_{right_base}{ext}")
    
    # 간접 조인인 경우 중간 테이블 처리
    if use_indirect:
        # 중간 테이블 읽기
        middle_data = {}
        middle_fieldnames = None
        
        with open(middle_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            middle_fieldnames = list(reader.fieldnames)
            
            # 중간 테이블의 키 찾기
            left_to_middle = None
            middle_id = None
            middle_to_right = None
            
            # left_key를 참조하는 컬럼 찾기 (예: VocabularyId)
            # Vocabulary.Id -> Meaning.VocabularyId
            for col in middle_fieldnames:
                # Id를 VocabularyId로 변환하거나, VocabularyId 컬럼 찾기
                if left_key.lower() == 'id':
                    # Vocabulary의 Id를 찾는 경우 -> VocabularyId 컬럼 찾기
                    if 'vocabulary' in col.lower() and 'id' in col.lower():
                        left_to_middle = col
                        break
                elif left_key.lower() in col.lower() or col.lower() in left_key.lower():
                    if 'id' in col.lower():
                        left_to_middle = col
                        break
            
            # middle_id 찾기 (Meaning의 Id)
            if 'Id' in middle_fieldnames:
                middle_id = 'Id'
            
            # right_key를 참조하는 컬럼 찾기 (예: MeaningId)
            # Example.MeaningId -> Meaning.Id
            # right_key가 MeaningId인 경우, 중간 테이블의 Id를 사용
            if right_key.lower() == 'meaningid' or ('meaning' in right_key.lower() and 'id' in right_key.lower()):
                # MeaningId는 중간 테이블의 Id를 참조
                middle_to_right = middle_id  # Meaning.Id
            else:
                # 다른 경우 컬럼에서 찾기
                for col in middle_fieldnames:
                    if right_key.lower() in col.lower() or col.lower() in right_key.lower():
                        if 'id' in col.lower():
                            middle_to_right = col
                            break
            
            if not left_to_middle or not middle_id:
                print(f"오류: 중간 테이블에서 조인 키를 찾을 수 없습니다.")
                sys.exit(1)
            
            # 중간 테이블 인덱스 생성 (left_to_middle -> middle_id)
            for row in reader:
                key = row.get(left_to_middle, '').strip()
                mid_id = row.get(middle_id, '').strip()
                if key and mid_id:
                    if key not in middle_data:
                        middle_data[key] = []
                    middle_data[key].append((mid_id, row))
        
        print(f"중간 테이블: {len(middle_data)}개의 고유 키, {sum(len(rows) for rows in middle_data.values())}개 행")
        
        # 오른쪽 파일 읽기 (middle_id를 키로)
        right_data = {}
        right_fieldnames = None
        
        with open(right_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            right_fieldnames = list(reader.fieldnames)
            
            # right_key가 실제로는 middle_to_right를 참조
            actual_right_key = middle_to_right if middle_to_right in right_fieldnames else right_key
            
            if actual_right_key not in right_fieldnames:
                print(f"오류: '{right_file}'에 '{actual_right_key}' 컬럼이 없습니다.")
                print(f"사용 가능한 컬럼: {', '.join(right_fieldnames)}")
                sys.exit(1)
            
            for row in reader:
                key = row.get(actual_right_key, '').strip()
                if key:
                    if key not in right_data:
                        right_data[key] = []
                    right_data[key].append(row)
        
        print(f"오른쪽 파일: {len(right_data)}개의 고유 키, {sum(len(rows) for rows in right_data.values())}개 행")
        
        # 간접 조인 수행
        left_fieldnames = None
        joined_rows = []
        left_only_count = 0
        right_only_count = 0
        matched_count = 0
        
        with open(left_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            left_fieldnames = list(reader.fieldnames)
            
            if left_key not in left_fieldnames:
                print(f"오류: '{left_file}'에 '{left_key}' 컬럼이 없습니다.")
                print(f"사용 가능한 컬럼: {', '.join(left_fieldnames)}")
                sys.exit(1)
            
            # 출력 컬럼명 생성
            output_fieldnames = list(left_fieldnames)
            for col in middle_fieldnames:
                if col != left_to_middle and col != middle_id:
                    if col not in output_fieldnames:
                        output_fieldnames.append(col)
                    else:
                        output_fieldnames.append(f"{col}_middle")
            for col in right_fieldnames:
                if col != actual_right_key:
                    if col not in output_fieldnames:
                        output_fieldnames.append(col)
                    else:
                        output_fieldnames.append(f"{col}_right")
            
            for row in reader:
                key = row.get(left_key, '').strip()
                
                if not key:
                    if join_type in ['left', 'full']:
                        new_row = dict(row)
                        for col in middle_fieldnames:
                            if col != left_to_middle and col != middle_id:
                                new_col = col if col not in new_row else f"{col}_middle"
                                new_row[new_col] = ''
                        for col in right_fieldnames:
                            if col != actual_right_key:
                                new_col = col if col not in new_row else f"{col}_right"
                                new_row[new_col] = ''
                        joined_rows.append(new_row)
                        left_only_count += 1
                    continue
                
                # 중간 테이블에서 매칭
                if key in middle_data:
                    for mid_id, middle_row in middle_data[key]:
                        # 오른쪽 테이블에서 매칭
                        if mid_id in right_data:
                            for right_row in right_data[mid_id]:
                                new_row = dict(row)
                                # 중간 테이블 데이터 추가
                                for col in middle_fieldnames:
                                    if col != left_to_middle and col != middle_id:
                                        new_col = col if col not in new_row else f"{col}_middle"
                                        new_row[new_col] = middle_row.get(col, '')
                                # 오른쪽 테이블 데이터 추가
                                for col in right_fieldnames:
                                    if col != actual_right_key:
                                        new_col = col if col not in new_row else f"{col}_right"
                                        new_row[new_col] = right_row.get(col, '')
                                joined_rows.append(new_row)
                                matched_count += 1
                        else:
                            # 중간은 있지만 오른쪽이 없음
                            if join_type in ['left', 'full']:
                                new_row = dict(row)
                                for col in middle_fieldnames:
                                    if col != left_to_middle and col != middle_id:
                                        new_col = col if col not in new_row else f"{col}_middle"
                                        new_row[new_col] = middle_row.get(col, '')
                                for col in right_fieldnames:
                                    if col != actual_right_key:
                                        new_col = col if col not in new_row else f"{col}_right"
                                        new_row[new_col] = ''
                                joined_rows.append(new_row)
                                left_only_count += 1
                else:
                    # 왼쪽에만 있음
                    if join_type in ['left', 'full']:
                        new_row = dict(row)
                        for col in middle_fieldnames:
                            if col != left_to_middle and col != middle_id:
                                new_col = col if col not in new_row else f"{col}_middle"
                                new_row[new_col] = ''
                        for col in right_fieldnames:
                            if col != actual_right_key:
                                new_col = col if col not in new_row else f"{col}_right"
                                new_row[new_col] = ''
                        joined_rows.append(new_row)
                        left_only_count += 1
        
        # RIGHT JOIN 또는 FULL JOIN 처리
        if join_type in ['right', 'full']:
            matched_left_keys = set()
            matched_middle_ids = set()
            
            with open(left_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = row.get(left_key, '').strip()
                    if key and key in middle_data:
                        for mid_id, _ in middle_data[key]:
                            matched_left_keys.add(key)
                            matched_middle_ids.add(mid_id)
            
            for mid_id, right_rows in right_data.items():
                if mid_id not in matched_middle_ids:
                    for right_row in right_rows:
                        new_row = {}
                        for col in left_fieldnames:
                            new_row[col] = ''
                        for col in middle_fieldnames:
                            if col != left_to_middle and col != middle_id:
                                new_col = col if col not in new_row else f"{col}_middle"
                                new_row[new_col] = ''
                        for col in right_fieldnames:
                            if col != actual_right_key:
                                new_col = col if col not in new_row else f"{col}_right"
                                new_row[new_col] = right_row.get(col, '')
                        joined_rows.append(new_row)
                        right_only_count += 1
        
        # 결과 저장
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(joined_rows)
        
        print(f"\n조인 완료! (간접 조인)")
        print(f"  왼쪽 파일: {left_file}")
        print(f"  중간 파일: {middle_file}")
        print(f"  오른쪽 파일: {right_file}")
        print(f"  조인 경로: {left_key} -> {left_to_middle} -> {middle_id} -> {middle_to_right}")
        print(f"  조인 타입: {join_type}")
        print(f"  출력 파일: {output_file}")
        print(f"\n통계:")
        print(f"  총 조인된 행: {len(joined_rows)}개")
        print(f"  매칭된 행: {matched_count}개")
        if join_type in ['left', 'full']:
            print(f"  왼쪽에만 있는 행: {left_only_count}개")
        if join_type in ['right', 'full']:
            print(f"  오른쪽에만 있는 행: {right_only_count}개")
        
        return
    
    # 직접 조인 (기존 로직)
    # 오른쪽 파일 읽기 (인덱스 생성)
    right_data = {}
    right_fieldnames = None
    
    with open(right_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        right_fieldnames = list(reader.fieldnames)
        
        if right_key not in right_fieldnames:
            print(f"오류: '{right_file}'에 '{right_key}' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(right_fieldnames)}")
            sys.exit(1)
        
        for row in reader:
            key = row.get(right_key, '').strip()
            if key:
                if key not in right_data:
                    right_data[key] = []
                right_data[key].append(row)
    
    print(f"오른쪽 파일: {len(right_data)}개의 고유 키, {sum(len(rows) for rows in right_data.values())}개 행")
    
    # 왼쪽 파일 읽기 및 조인
    left_fieldnames = None
    joined_rows = []
    left_only_count = 0
    right_only_count = 0
    matched_count = 0
    
    with open(left_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        left_fieldnames = list(reader.fieldnames)
        
        if left_key not in left_fieldnames:
            print(f"오류: '{left_file}'에 '{left_key}' 컬럼이 없습니다.")
            print(f"사용 가능한 컬럼: {', '.join(left_fieldnames)}")
            sys.exit(1)
        
        # 출력 컬럼명 생성 (중복 제거)
        # 왼쪽 파일명에서 테이블명 추출
        left_table_name = os.path.splitext(os.path.basename(left_file))[0]
        right_table_name = os.path.splitext(os.path.basename(right_file))[0]
        
        # 왼쪽 컬럼: Id는 {파일명}Id로 변경
        output_fieldnames = []
        for col in left_fieldnames:
            if col == left_key and col.lower() == 'id':
                # Id 컬럼은 파일명Id로 변경
                output_fieldnames.append(f"{left_table_name}Id")
            else:
                output_fieldnames.append(col)
        
        # 오른쪽 컬럼 추가 (중복 제거)
        for col in right_fieldnames:
            if col == right_key:
                # 키 컬럼은 제외 (이미 왼쪽에 있거나 조인 키로 사용됨)
                continue
            elif col.lower() == 'id':
                # Id 컬럼은 파일명Id로 변경
                new_col = f"{right_table_name}Id"
                if new_col not in output_fieldnames:
                    output_fieldnames.append(new_col)
                # 이미 있으면 제외 (중복 제거)
            else:
                # 중복 컬럼은 제외 (왼쪽 것만 유지)
                if col not in output_fieldnames:
                    output_fieldnames.append(col)
                # 이미 있으면 제외 (중복 제거)
        
        for row in reader:
            key = row.get(left_key, '').strip()
            
            if not key:
                # 키가 없으면 조인 타입에 따라 처리
                if join_type in ['left', 'full']:
                    # 오른쪽 컬럼은 None으로 채움
                    new_row = dict(row)
                    # 왼쪽의 Id를 파일명Id로 변경
                    if left_key.lower() == 'id' and left_key in new_row:
                        new_row[f"{left_table_name}Id"] = new_row.pop(left_key)
                    
                    for col in right_fieldnames:
                        if col != right_key:
                            if col.lower() == 'id':
                                new_col = f"{right_table_name}Id"
                                # 중복이면 제외 (이미 왼쪽에 있음)
                                if new_col not in new_row:
                                    new_row[new_col] = ''
                            else:
                                # 중복이면 제외 (이미 왼쪽에 있음)
                                if col not in new_row:
                                    new_row[col] = ''
                    joined_rows.append(new_row)
                    left_only_count += 1
                continue
            
            # 오른쪽에서 매칭되는 행 찾기
            if key in right_data:
                # 매칭됨: 조인
                for right_row in right_data[key]:
                    new_row = dict(row)
                    # 왼쪽의 Id를 파일명Id로 변경
                    if left_key.lower() == 'id' and left_key in new_row:
                        new_row[f"{left_table_name}Id"] = new_row.pop(left_key)
                    
                    for col in right_fieldnames:
                        if col != right_key:
                            if col.lower() == 'id':
                                # Id는 파일명Id로 변경
                                new_col = f"{right_table_name}Id"
                                # 중복이면 제외 (이미 왼쪽에 있음)
                                if new_col not in new_row:
                                    new_row[new_col] = right_row.get(col, '')
                            else:
                                # 중복이면 제외 (이미 왼쪽에 있음)
                                if col not in new_row:
                                    new_row[col] = right_row.get(col, '')
                    joined_rows.append(new_row)
                    matched_count += 1
            else:
                # 매칭 안됨
                if join_type in ['left', 'full']:
                    # 왼쪽만 포함
                    new_row = dict(row)
                    # 왼쪽의 Id를 파일명Id로 변경
                    if left_key.lower() == 'id' and left_key in new_row:
                        new_row[f"{left_table_name}Id"] = new_row.pop(left_key)
                    
                    for col in right_fieldnames:
                        if col != right_key:
                            if col.lower() == 'id':
                                new_col = f"{right_table_name}Id"
                                if new_col in new_row:
                                    new_col = f"{new_col}_right"
                            else:
                                new_col = col if col not in new_row else f"{col}_right"
                            new_row[new_col] = ''
                    joined_rows.append(new_row)
                    left_only_count += 1
    
    # RIGHT JOIN 또는 FULL JOIN: 오른쪽에만 있는 행 추가
    if join_type in ['right', 'full']:
        matched_keys = set()
        with open(left_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get(left_key, '').strip()
                if key:
                    matched_keys.add(key)
        
        for key, right_rows in right_data.items():
            if key not in matched_keys:
                # 오른쪽에만 있는 행
                for right_row in right_rows:
                    new_row = {}
                    # 왼쪽 컬럼은 빈 값으로 채움
                    for col in left_fieldnames:
                        if col == left_key and col.lower() == 'id':
                            new_row[f"{left_table_name}Id"] = key
                        else:
                            new_row[col] = ''
                    # 오른쪽 컬럼 추가 (중복 제거)
                    for col in right_fieldnames:
                        if col != right_key:
                            if col.lower() == 'id':
                                new_col = f"{right_table_name}Id"
                                # 중복이면 제외 (이미 왼쪽에 있음)
                                if new_col not in new_row:
                                    new_row[new_col] = right_row.get(col, '')
                            else:
                                # 중복이면 제외 (이미 왼쪽에 있음)
                                if col not in new_row:
                                    new_row[col] = right_row.get(col, '')
                    joined_rows.append(new_row)
                    right_only_count += 1
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(joined_rows)
    
    print(f"\n조인 완료!")
    print(f"  왼쪽 파일: {left_file}")
    print(f"  오른쪽 파일: {right_file}")
    print(f"  조인 키: {left_key} = {right_key}")
    print(f"  조인 타입: {join_type}")
    print(f"  출력 파일: {output_file}")
    print(f"\n통계:")
    print(f"  총 조인된 행: {len(joined_rows)}개")
    print(f"  매칭된 행: {matched_count}개")
    if join_type in ['left', 'full']:
        print(f"  왼쪽에만 있는 행: {left_only_count}개")
    if join_type in ['right', 'full']:
        print(f"  오른쪽에만 있는 행: {right_only_count}개")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("사용법: python script/join_csv.py <left_file.csv> <right_file.csv> <left_key> <right_key> [middle_file.csv] [join_type] [output_file]")
        print("예시: python script/join_csv.py Vocabulary.csv Meaning.csv Id VocabularyId")
        print("      python script/join_csv.py Vocabulary.csv Example.csv Id MeaningId")
        print("      python script/join_csv.py Vocabulary.csv Example.csv Id MeaningId Meaning.csv")
        print("      python script/join_csv.py Vocabulary.csv Example.csv Id MeaningId Meaning.csv left output.csv")
        print("\n조인 타입:")
        print("  inner: 양쪽 모두에 있는 행만 (기본값)")
        print("  left: 왼쪽 파일의 모든 행 + 오른쪽 매칭")
        print("  right: 오른쪽 파일의 모든 행 + 왼쪽 매칭")
        print("  full: 양쪽 파일의 모든 행")
        print("\n참고: 오른쪽 파일에 직접 키가 없으면 자동으로 중간 테이블을 찾아 간접 조인합니다.")
        sys.exit(1)
    
    left_file = sys.argv[1]
    right_file = sys.argv[2]
    left_key = sys.argv[3]
    right_key = sys.argv[4]
    
    # 중간 파일, 조인 타입, 출력 파일 파싱
    middle_file = None
    join_type = 'inner'
    output_file = None
    
    args = sys.argv[5:]
    for arg in args:
        if arg in ['inner', 'left', 'right', 'full']:
            join_type = arg
        elif arg.endswith('.csv'):
            if middle_file is None and os.path.exists(arg):
                middle_file = arg
            else:
                output_file = arg
        else:
            print(f"경고: '{arg}'는 무시됩니다.")
    
    join_csv_files(left_file, right_file, left_key, right_key, middle_file, join_type, output_file)

