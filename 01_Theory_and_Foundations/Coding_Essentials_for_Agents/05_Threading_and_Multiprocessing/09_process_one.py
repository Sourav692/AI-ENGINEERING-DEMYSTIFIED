"""
=============================================================================
GIL LIMITATION: CPU-HEAVY WORK WITH THREADING (SLOW!)
=============================================================================

The Problem:
------------
This script runs CPU-intensive work in 2 threads, but it WON'T be faster
than running sequentially! Why? The Global Interpreter Lock (GIL)!

What's Happening:
-----------------
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Python Process (ONE GIL)                                           │
    │  ┌─────────────────────────────────────────────────────────────┐    │
    │  │ Thread 1: ████░░░░████░░░░████░░░░████░░░░ (CPU work)       │    │
    │  │ Thread 2: ░░░░████░░░░████░░░░████░░░░████ (CPU work)       │    │
    │  │                ↑         ↑         ↑                        │    │
    │  │                └── GIL switches every ~5ms ──┘              │    │
    │  └─────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────┘

    Even with 2 threads, only ONE runs at a time!
    Total time ≈ Sequential time (or even WORSE due to overhead)

This Script Demonstrates:
-------------------------
- 2 threads performing CPU-heavy calculations
- Each thread sums numbers from 0 to 10 million
- Despite having 2 threads, there's NO speedup due to GIL!

Compare with 10_process_two.py:
-------------------------------
Using multiprocessing instead of threading will show actual speedup
because each process has its OWN GIL!

=============================================================================
"""

import threading  # Threading module
import time       # For measuring execution time


def cpu_heavy():
    """
    A CPU-BOUND function that performs intensive calculation.
    
    This function:
    - Does pure computation (no I/O)
    - Holds the GIL while executing
    - Blocks other threads from running Python bytecode
    
    With threading, this is the WORST case scenario for the GIL!
    """
    print(f"🔢 Crunching some numbers...")
    
    # CPU-intensive work: sum of 0 to 10 million
    # This is pure computation - no I/O, no waiting
    # The GIL is held throughout this loop!
    total = 0
    for i in range(10**7):  # 10 million iterations
        total += i
    
    print("DONE ✅")


# =============================================================================
# RUN CPU-HEAVY WORK IN 2 THREADS
# =============================================================================

print("=" * 60)
print("🐢 GIL LIMITATION: CPU Work with Threading (SLOW!)")
print("=" * 60)
print("Running 2 CPU-heavy tasks in threads...")
print("Watch how threading DOESN'T speed this up!\n")

start = time.time()

# Create 2 threads for CPU-heavy work
threads = [threading.Thread(target=cpu_heavy) for _ in range(2)]

# Start all threads
[t.start() for t in threads]

# Wait for all threads to complete
[t.join() for t in threads]

elapsed = time.time() - start
print(f"\n⏱️  Time taken: {elapsed:.2f} seconds")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🐢 GIL LIMITATION: CPU Work with Threading (SLOW!)
# ============================================================
# Running 2 CPU-heavy tasks in threads...
# Watch how threading DOESN'T speed this up!
#
# 🔢 Crunching some numbers...
# 🔢 Crunching some numbers...
# DONE ✅
# DONE ✅
#
# ⏱️  Time taken: 1.50 seconds  ← Similar to sequential execution!
#
# If parallelism worked: ~0.75 seconds (half the time)
# Actual result: ~1.5 seconds (no speedup due to GIL!)
#
# =============================================================================

# =============================================================================
# WHY THREADING FAILS FOR CPU-BOUND WORK
# =============================================================================
#
# 1. GIL (Global Interpreter Lock):
#    Only ONE thread can execute Python bytecode at a time
#
# 2. CPU-bound work HOLDS the GIL:
#    Unlike I/O operations, CPU work doesn't release the GIL
#
# 3. Thread switching overhead:
#    GIL switches every ~5ms, adding overhead without benefit
#
# 4. No parallelism:
#    2 threads on 2 CPU cores, but only 1 core is ever used!
#
# THE SOLUTION: Use multiprocessing for CPU-bound work!
# See 10_process_two.py for the fast version!
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Threading does NOT speed up CPU-bound work in Python
# 2. The GIL limits threads to one-at-a-time execution
# 3. For CPU-bound work, use multiprocessing (each process has own GIL)
# 4. Threading is still great for I/O-bound work (network, file, etc.)
# 5. This is a fundamental limitation of CPython
#
# =============================================================================