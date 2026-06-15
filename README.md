# StorPool quiz

My solutions to the four-task quiz.

## Setup

```
pip install -e .
```

Tested on Python 3.9.

## 1. Counting — `1_memory_efficient_counting.py`

I create a 4GB list where I can store solutions, 8 bits per slot.
I use 8 bits because I need to track 3 states, and 8 is the smallest unit numpy handles natively —
going smaller (2 bits) is possible but means manual bit shifts that don't vectorize well.
Then I use numpy because it's faster than Python.
I process the data in chunks and use np.unique(chunk, return_counts=True) to get the unique values and their counts.
I use that because numpy processes operations in stages, and the write stage has no context of the other processes —
so duplicates in a chunk would overwrite each other instead of accumulating.
For 10M ints we process the data in 4 for 1B it would take up to 15 minutes.

## 2. FizzBuzz without conditionals or loops — `2_fizzbuzz_with_a_catch.py`

Print 1-100, replacing multiples of 3 with `A`, multiples of 5 with `B`, multiples of 15 with `AB`. No `if`, `for`, `while`, ternary, `try/except`, list comprehensions — anything that branches.

A tuple/dict indexed by a boolean replaces `if` — booleans in Python are subclasses of `int`, so `(a, b)[some_condition]` picks one. Recursion replaces the loop. Picking the output: a dict keyed by `(n%3==0, n%5==0)` with `.get(key, n)` defaulting to the number itself. Stopping recursion: a dispatch dict `{False: keep_going, True: lambda *_: None}` keyed by `n > 100`.

## 3. Disk model counts — `3_analyze_uncompressed_json.py`

I decompressed the bz2 once with lbzip2 -dc (parallel decompression, 1-2 mins for the 2.7 GB compressed → 21 GB JSON).
I then split the file into N byte ranges, one per worker, nudging each boundary forward to the next },{ so no record gets split across chunks.
Each worker reads only its byte range and scans for "model":"..." with a regex instead of full JSON parsing — the structure is regular enough that regex is
correct and 10× faster than json.loads. I used multiprocessing.Pool with imap_unordered (capped at cpu_count() - 2 so the OS stays responsive)
and aggregated the partial Counters. Total runtime: 1m15s on 21 GB of JSON, returning 13 models with ~33M occurrences each.

## 4. Reverse engineering

Two stripped Linux x86-64 ELF binaries that segfault on launch.

**Binary `a`:** opens `./pesho`, reads up to 1024 bytes, `malloc(N)` where N is the actual bytes read, then `memcpy(dst, src, 1024)` — a fixed 1024, regardless of N. With a file smaller than 1024 bytes the memcpy overflows the heap and glibc aborts. With `./pesho` ≥ 1024 bytes it runs cleanly and prints each byte as a signed integer.

**Binary `b`:** reads `$TMPDIR`, counts whether it starts with `/`, prints `Init done N .`, then prompts for a password. Dereferences the `getenv()` return without checking for NULL, so it crashes whenever `TMPDIR` is unset.

How I worked them out: gdb backtrace → faulting instruction + register state → walk the few instructions around it → identify glibc calls (`open`, `read`, `malloc`, `getenv`) by argument shape and call order → pull the rodata strings with `gdb -batch -ex 'x/s 0x...'` to confirm intent → run with the right inputs to verify.

Apple Silicon side note: x86-64 binaries under QEMU break gdb's ptrace, so I moved the investigation to GitHub Codespaces (real x86-64 Linux).
