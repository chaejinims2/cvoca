#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from collections import defaultdict

word_defs = defaultdict(set)

with open('data/Meaning_removed.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        word_id = int(row['word_id'])
        def_id = int(row['DefId']) if row['DefId'] and row['DefId'].lower() != 'null' else 0
        word_defs[word_id].add(def_id)

max_defs = max([len(v) for v in word_defs.values()])
max_word_id = max(word_defs.keys())
max_def_id = max([max(v) for v in word_defs.values()])

print(f'Max word_id: {max_word_id}')
print(f'Max DefId count per word: {max_defs}')
print(f'Max DefId value: {max_def_id}')
print('\nWords with most DefIds:')
for w, defs in sorted(word_defs.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print(f'  word_id {w}: {len(defs)} DefIds {sorted(defs)}')

