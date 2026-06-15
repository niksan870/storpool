"""
I decompressed the bz2 once with lbzip2 -dc (parallel decompression, 1-2 mins for the 2.7 GB compressed → 21 GB JSON).
I then split the file into N byte ranges, one per worker, nudging each boundary forward to the next },{ so no record gets split across chunks.
Each worker reads only its byte range and scans for "model":"..." with a regex instead of full JSON parsing — the structure is regular enough that regex is
correct and 10× faster than json.loads. I used multiprocessing.Pool with imap_unordered (capped at cpu_count() - 2 so the OS stays responsive)
and aggregated the partial Counters. Total runtime: 1m15s on 21 GB of JSON, returning 13 models with ~33M occurrences each.
"""
import re
import os
from collections import Counter
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

MODEL_RE = re.compile(rb'"model":"([^"]+)"')


def find_safe_boundary(path, offset):
    with open(path, "rb") as f:
        f.seek(offset)
        chunk = f.read(4096)
        return offset + chunk.find(b"},{") + 1


def count_in_range(args):
    path, start, end = args
    with open(path, "rb") as f:
        f.seek(start)
        data = f.read(end - start)
    return Counter(m.decode() for m in MODEL_RE.findall(data))



if __name__ == "__main__":
    path = "bigf.json"
    size = os.path.getsize(path)
    N = max(1, cpu_count() - 2)
    raw = [size * i // N for i in range(N + 1)]
    safe = [1] + [find_safe_boundary(path, x) for x in raw[1:-1]] + [size - 1]
    chunks = [(path, safe[i], safe[i + 1]) for i in range(N)]
    with Pool(N) as pool:
        partials = list(tqdm(
            pool.imap_unordered(count_in_range, chunks),
            total=len(chunks),
            desc="parsing chunks"
        ))
    total = sum(partials, Counter())
    print(len(total), total.most_common(10))
