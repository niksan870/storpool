"""
I create a 4GB list where I can store solutions, 8 bits per slot.
I use 8 bits because I need to track 3 states, and 8 is the smallest unit numpy handles natively —
going smaller (2 bits) is possible but means manual bit shifts that don't vectorize well.
Then I use numpy because it's faster than Python.
I process the data in chunks and use np.unique(chunk, return_counts=True) to get the unique values and their counts.
I use that because numpy processes operations in stages, and the write stage has no context of the other processes —
so duplicates in a chunk would overwrite each other instead of accumulating.
For 10M ints we process the data in 4 for 1B it would take up to 15 minutes.
"""

import time

import numpy as np
from enum import IntEnum

CHUNK_SIZE = 10_000_000


class SeenState(IntEnum):
    NEVER_SEEN = 0
    SEEN_ONCE = 1
    SEEN_MANY = 2


with open("test_medium.bin", "rb") as f:
    t0 = time.perf_counter()
    state = np.zeros(2 ** 32, dtype=np.uint8)
    while True:
        chunk = np.fromfile(f, dtype=np.uint32, count=CHUNK_SIZE)
        if chunk.size == 0:
            break
        unique_vals, counts = np.unique(chunk, return_counts=True)
        counts_capped = np.minimum(counts, SeenState.SEEN_MANY)
        new_state = state[unique_vals].astype(np.int32) + counts_capped
        state[unique_vals] = np.minimum(new_state, SeenState.SEEN_MANY).astype(np.uint8)

    print("unique:", np.count_nonzero(state >= 1))
    print("once:  ", np.count_nonzero(state == 1))
    print(f"took {time.perf_counter() - t0:.2f}s")

if __name__ == '__main__':
    pass
