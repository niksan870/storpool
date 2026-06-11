import numpy as np
from collections import Counter

np.random.seed(42)
values = np.random.randint(0, 2 ** 32, size=10_000_000, dtype=np.uint32)
values.tofile("test_medium.bin")

counts = Counter(values.tolist())
print(f"Wrote {values.nbytes} bytes to test_medium.bin")
print(f"Expected: unique={len(counts)}, once={sum(1 for c in counts.values() if c == 1)}")
