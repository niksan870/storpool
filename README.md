# StorPool quiz

My solutions to the four-task quiz. Python where it made sense.

## Setup

```
pip install -e .
```

Tested on Python 3.9.

## 1. Counting — `1_memory_efficient_counting.py`

Count unique uint32 values, and values seen exactly once, in a 4 GB binary file of 1 billion uint32s.

Approach: one 4 GB uint8 array indexed by value, holding `0/1/2` for never/once/many. Stream the file in 10M chunks, use `np.unique(chunk, return_counts=True)` per chunk to dedupe, add capped counts. At the end, `count(state >= 1)` is unique and `count(state == 1)` is seen-once. Same array answers both.

Why 8 bits per slot: I only need 3 states, but 2-bit packing is hard to vectorize in Python, and a full uint32 wastes 4× the RAM. uint8 is the practical sweet spot.

Why dedupe inside each chunk: numpy reads all positions before it writes any, so `state[chunk] += 1` collapses duplicate indices instead of accumulating. `np.unique` avoids that.

Timing: 10M values in ~4s. 1B extrapolates to ~7-8 min.

## 2. FizzBuzz without conditionals or loops — `2_fizzbuzz_with_a_catch.py`

Print 1-100, replacing multiples of 3 with `A`, multiples of 5 with `B`, multiples of 15 with `AB`. No `if`, `for`, `while`, ternary, `try/except`, list comprehensions — anything that branches.

Approach: a tuple indexed by a boolean replaces `if` — booleans in Python are subclasses of `int`, so `(a, b)[some_condition]` picks one. Recursion replaces the loop. Picking the output: a dict keyed by `(n%3==0, n%5==0)` with `.get(key, n)` defaulting to the number itself. Stopping recursion: a 2-tuple of functions `(keep_going, stop)` indexed by `n > 100`, then called.

## 3. Disk model counts — `3_analyze_uncompressed_json.py`

Count distinct disk models in `bigf.json.bz2` and how often each appears.

Approach: decompress once (`lbzip2 -dc bigf.json.bz2 > bigf.json` — ~30s for 2.7 GB → 21 GB). Split the file into N byte ranges, one per worker. Each boundary is nudged forward to the next `},{` so no record is split. Each worker scans its range with a regex (`"model":"..."`) instead of `json.loads` — the structure is regular enough that regex is correct and ~10× faster. `multiprocessing.Pool` with `imap_unordered`, capped at `cpu_count() - 2`. Aggregate Counters at the end.

Timing: ~1m15s on 21 GB. 13 distinct models, ~33M occurrences each.

## 4. Reverse engineering

Two stripped Linux x86-64 ELF binaries that segfault on launch.

**Binary `a`:** opens `./pesho`, reads up to 1024 bytes, `malloc(N)` where N is the actual bytes read, then `memcpy(dst, src, 1024)` — a fixed 1024, regardless of N. With a file smaller than 1024 bytes the memcpy overflows the heap and glibc aborts. With `./pesho` ≥ 1024 bytes it runs cleanly and prints each byte as a signed integer.

**Binary `b`:** reads `$TMPDIR`, counts whether it starts with `/`, prints `Init done N .`, then prompts for a password. Dereferences the `getenv()` return without checking for NULL, so it crashes whenever `TMPDIR` is unset.

How I worked them out: gdb backtrace → faulting instruction + register state → walk the few instructions around it → identify glibc calls (`open`, `read`, `malloc`, `getenv`) by argument shape and call order → pull the rodata strings with `gdb -batch -ex 'x/s 0x...'` to confirm intent → run with the right inputs to verify.

Apple Silicon side note: x86-64 binaries under QEMU break gdb's ptrace, so I moved the investigation to GitHub Codespaces (real x86-64 Linux).
