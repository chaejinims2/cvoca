#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Means.csv와 Exams.csv의 sense_no 매핑을 확인하는 스크립트
"""

import csv
import os

means_file = 'data/new/Means.csv'
exams_file = 'data/new/Exams.csv'

# Means.csv의 sense_no 수집
means_ids = set()
means_data = {}
with open(means_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['sense_no']:
            mean_id = int(row['sense_no'])
            means_ids.add(mean_id)
            means_data[mean_id] = row

# Exams.csv의 sense_no 수집
exams_ids = set()
exams_data = {}
with open(exams_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['sense_no']:
            mean_id = int(row['sense_no'])
            exams_ids.add(mean_id)
            exams_data[mean_id] = row

# 차이점 찾기
only_in_means = means_ids - exams_ids
only_in_exams = exams_ids - means_ids
common = means_ids & exams_ids

print(f"Means.csv sense_no 개수: {len(means_ids)}")
print(f"Exams.csv sense_no 개수: {len(exams_ids)}")
print(f"공통 sense_no 개수: {len(common)}")
print(f"\nMeans에만 있는 sense_no: {len(only_in_means)}개")
print(f"Exams에만 있는 sense_no: {len(only_in_exams)}개")

if only_in_means:
    print(f"\n=== Means에만 있는 sense_no (상위 20개) ===")
    for mean_id in sorted(list(only_in_means))[:20]:
        row = means_data[mean_id]
        print(f"  sense_no={mean_id}: word_id={row['word_id']}, DefId={row['DefId']}, definition={row['definition'][:30]}...")

if only_in_exams:
    print(f"\n=== Exams에만 있는 sense_no (상위 20개) ===")
    for mean_id in sorted(list(only_in_exams))[:20]:
        row = exams_data[mean_id]
        print(f"  sense_no={mean_id}: definition={row['definition'][:30]}...")

# 중복 확인
means_duplicates = {}
exams_duplicates = {}

means_list = []
with open(means_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['sense_no']:
            mean_id = int(row['sense_no'])
            means_list.append(mean_id)
            if mean_id in means_duplicates:
                means_duplicates[mean_id] += 1
            else:
                means_duplicates[mean_id] = 1

exams_list = []
with open(exams_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['sense_no']:
            mean_id = int(row['sense_no'])
            exams_list.append(mean_id)
            if mean_id in exams_duplicates:
                exams_duplicates[mean_id] += 1
            else:
                exams_duplicates[mean_id] = 1

means_dup = {k: v for k, v in means_duplicates.items() if v > 1}
exams_dup = {k: v for k, v in exams_duplicates.items() if v > 1}

if means_dup:
    print(f"\n=== Means.csv에서 중복된 sense_no ===")
    for mean_id, count in sorted(means_dup.items()):
        print(f"  sense_no={mean_id}: {count}번 나타남")

if exams_dup:
    print(f"\n=== Exams.csv에서 중복된 sense_no ===")
    for mean_id, count in sorted(exams_dup.items()):
        print(f"  sense_no={mean_id}: {count}번 나타남")

