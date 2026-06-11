"""
I stream the file with bz2.open and parse JSON incrementally with ijson.items because
the compressed file is 2.7 GB and uncompressed it's likely 10-30 GB - can't fit in memory.
I yield one disk record at a time and increment a Counter keyed by model.
Memory stays tiny because only one record is in scope plus the Counter (bounded by the number of distinct models).
At the end len(counter) gives the model count and counter.most_common() gives the per-model frequencies.
I stuck with ijson's default pure-Python backend for portability; switching to the yajl2 C backend would
cut runtime roughly in half but requires a system library (brew install yajl).
"""
import bz2
from collections import Counter

import ijson

counter = Counter()
with bz2.open("bigf.json.bz2", "rb") as f:
    for disk in ijson.items(f, "item"):
        counter[disk["model"]] += 1
    print(len(counter))
    print(counter.most_common(10))
