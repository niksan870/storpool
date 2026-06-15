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
