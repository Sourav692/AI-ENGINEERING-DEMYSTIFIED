"""
=============================================================================
BYPASSING THE GIL WITH MULTIPROCESSING
=============================================================================

The Problem (from 03_gil_threading.py):
---------------------------------------
Threading cannot speed up CPU-bound tasks because of the GIL (Global 
Interpreter Lock). Only one thread can execute Python bytecode at a time.

The Solution: MULTIPROCESSING
-----------------------------
Multiprocessing creates separate PROCESSES, not threads. Each process has:
- Its own Python interpreter
- Its own memory space
- Its own GIL ← This is the key!

Since each process has its own GIL, they can execute Python code 
TRULY in parallel on different CPU cores!

How GIL Affects Threading vs Multiprocessing:
---------------------------------------------

THREADING (GIL blocks parallelism):
┌─────────────────────────────────────────────────────────────────────────┐
│  Single Python Interpreter with ONE GIL                                 │
│  ┌──────────────┐    ┌──────────────┐                                   │
│  │   Thread 1   │◄──►│   Thread 2   │  ← Threads share the same GIL    │
│  └──────────────┘    └──────────────┘    Only ONE runs at a time!      │
└─────────────────────────────────────────────────────────────────────────┘

MULTIPROCESSING (GIL is bypassed):
┌──────────────────────────────┐    ┌──────────────────────────────┐
│  Process 1                   │    │  Process 2                   │
│  Own Python Interpreter      │    │  Own Python Interpreter      │
│  Own GIL ← Released!         │    │  Own GIL ← Released!         │
│  Own Memory                  │    │  Own Memory                  │
│  ┌────────────────────────┐  │    │  ┌────────────────────────┐  │
│  │ Runs on CPU Core 1     │  │    │  │ Runs on CPU Core 2     │  │
│  └────────────────────────┘  │    │  └────────────────────────┘  │
└──────────────────────────────┘    └──────────────────────────────┘
         ↑                                     ↑
         └──── TRUE PARALLEL EXECUTION! ───────┘

Expected Performance:
---------------------
Compare with 03_gil_threading.py (same task, same machine):

Threading (2 threads):    ~X seconds (no speedup, maybe slower!)
Multiprocessing (2 proc): ~X/2 seconds (nearly 2x faster!) ⚡

=============================================================================
"""

from multiprocessing import Process  # For creating separate processes
import time                          # For measuring execution time


def crunch_number():
    """
    A CPU-BOUND task: pure computation with no I/O.
    
    This is the SAME task as in 03_gil_threading.py!
    But now it runs in a SEPARATE PROCESS with its own GIL.
    
    Each process can use 100% of its assigned CPU core without
    being blocked by other processes!
    """
    print(f"🔢 Started the count process...")
    
    # =========================================================================
    # CPU-INTENSIVE WORK: Counting to 100 million
    # =========================================================================
    # This is identical to the threading example.
    # The difference is WHERE this code runs:
    #   - Threading: Same interpreter, same GIL → blocked by other threads
    #   - Multiprocessing: Own interpreter, own GIL → true parallelism!
    
    count = 0
    for _ in range(100_000_000):  # 100 million iterations
        count += 1
    
    print(f"✅ Ended the count process...")


# =============================================================================
# REQUIRED: if __name__ == "__main__" GUARD
# =============================================================================
# This prevents infinite process spawning on Windows.
# When a new process starts, it imports this module; without the guard,
# it would try to spawn more processes, causing an infinite loop!

if __name__ == "__main__":
    
    print("=" * 60)
    print("🧪 GIL BYPASS: CPU-bound task with Multiprocessing")
    print("=" * 60)
    print("Running 2 processes, each counting to 100 million...")
    print("Compare this with 03_gil_threading.py!\n")
    
    start = time.time()

    # =========================================================================
    # CREATE TWO SEPARATE PROCESSES
    # =========================================================================
    # Each Process object represents a completely separate Python instance
    # with its own interpreter and GIL
    
    p1 = Process(target=crunch_number)
    p2 = Process(target=crunch_number)

    # =========================================================================
    # START BOTH PROCESSES (TRUE PARALLEL EXECUTION!)
    # =========================================================================
    # Unlike threads, these processes run TRULY in parallel!
    # - p1 runs on one CPU core
    # - p2 runs on another CPU core
    # Both execute simultaneously, no GIL blocking!
    
    p1.start()  # Spawns a new Python process for p1
    p2.start()  # Spawns a new Python process for p2
    
    # =========================================================================
    # WAIT FOR BOTH PROCESSES TO COMPLETE
    # =========================================================================
    
    p1.join()   # Wait for p1 to finish
    p2.join()   # Wait for p2 to finish

    end = time.time()

    print(f"\n⏱️  Total time with multiprocessing: {end - start:.2f} seconds")


# =============================================================================
# EXPECTED RESULTS COMPARISON
# =============================================================================
#
# Running the SAME CPU-bound task (counting to 100 million, twice):
#
# ┌────────────────────────┬────────────────┬─────────────────────────────┐
# │ Approach               │ Time           │ Why?                        │
# ├────────────────────────┼────────────────┼─────────────────────────────┤
# │ Sequential (1 thread)  │ ~X seconds     │ Baseline                    │
# │ Threading (2 threads)  │ ~X seconds     │ GIL blocks parallelism ❌   │
# │ Multiprocessing (2)    │ ~X/2 seconds   │ True parallelism! ✅        │
# └────────────────────────┴────────────────┴─────────────────────────────┘
#
# Typical results on a multi-core machine:
#   Threading:       ~12-15 seconds
#   Multiprocessing: ~6-8 seconds  (nearly 2x faster!)
#
# =============================================================================

# =============================================================================
# VISUAL TIMELINE COMPARISON
# =============================================================================
#
# THREADING (GIL switching, no real parallelism):
# ───────────────────────────────────────────────
# Thread 1: ████░░░░████░░░░████░░░░████░░░░████
# Thread 2: ░░░░████░░░░████░░░░████░░░░████░░░░
#           |←────────── ~12 seconds ──────────→|
#
# MULTIPROCESSING (true parallelism):
# ────────────────────────────────────
# Process 1: ████████████████████████████████  (CPU Core 1)
# Process 2: ████████████████████████████████  (CPU Core 2)
#            |←────── ~6 seconds ───────→|
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
# 
# 1. Multiprocessing BYPASSES the GIL by using separate Python interpreters
# 2. Each process has its OWN GIL → no blocking between processes
# 3. True parallel execution on multiple CPU cores
# 4. For CPU-bound tasks: Multiprocessing >> Threading
# 5. Trade-off: Higher memory usage (each process has own memory space)
# 
# When to use what:
# ─────────────────
# I/O-bound tasks (waiting)  → Threading ✅ (lower overhead, shared memory)
# CPU-bound tasks (computing) → Multiprocessing ✅ (bypasses GIL)
#
# =============================================================================

# =============================================================================
# BONUS: OVERHEAD CONSIDERATIONS
# =============================================================================
#
# Multiprocessing has higher overhead than threading:
#   - Process creation is slower than thread creation
#   - No shared memory (need IPC: Queue, Pipe, Manager)
#   - More memory usage (each process copies the program)
#
# For small tasks, this overhead may negate the parallelism benefits.
# Multiprocessing shines for computationally heavy tasks!
#
# =============================================================================
