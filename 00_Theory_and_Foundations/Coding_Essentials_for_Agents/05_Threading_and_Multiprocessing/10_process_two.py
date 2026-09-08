"""
=============================================================================
GIL BYPASS: CPU-HEAVY WORK WITH MULTIPROCESSING (FAST!)
=============================================================================

The Solution:
-------------
This script runs the SAME CPU-intensive work as 09_process_one.py,
but uses MULTIPROCESSING instead of threading. Result? TRUE PARALLELISM!

What's Happening:
-----------------
    ┌──────────────────────────────────┐  ┌──────────────────────────────────┐
    │  Process 1                       │  │  Process 2                       │
    │  Own Python Interpreter          │  │  Own Python Interpreter          │
    │  Own GIL                         │  │  Own GIL                         │
    │  ┌────────────────────────────┐  │  │  ┌────────────────────────────┐  │
    │  │ CPU Core 1                 │  │  │  │ CPU Core 2                 │  │
    │  │ ██████████████████████████ │  │  │  │ ██████████████████████████ │  │
    │  │ (100% utilized!)           │  │  │  │ (100% utilized!)           │  │
    │  └────────────────────────────┘  │  │  └────────────────────────────┘  │
    └──────────────────────────────────┘  └──────────────────────────────────┘
                            ↑                               ↑
                            └───── TRUE PARALLEL EXECUTION ─┘

    Each process has its OWN GIL → No blocking between processes!

Comparison with Threading (09_process_one.py):
----------------------------------------------
    Threading (2 threads):      ~X seconds (GIL blocks parallelism)
    Multiprocessing (2 procs):  ~X/2 seconds (true parallelism!)

This Script Demonstrates:
-------------------------
- 2 processes performing CPU-heavy calculations
- Each process sums numbers from 0 to 1 BILLION (10x more than threading example!)
- Despite more work, it completes faster due to parallelism!

=============================================================================
"""

from multiprocessing import Process  # For creating separate processes
import time                          # For measuring execution time


def cpu_heavy():
    """
    A CPU-BOUND function that performs intensive calculation.
    
    This is similar to the threading example, but runs in a SEPARATE PROCESS.
    Each process has:
    - Its own Python interpreter
    - Its own GIL (no competition!)
    - Its own memory space
    - Access to a dedicated CPU core
    
    Result: TRUE parallel execution!
    """
    print(f"🔢 Crunching some numbers...")
    
    # CPU-intensive work: sum of 0 to 1 billion
    # This is 10x more work than the threading example!
    # But with multiprocessing, it's still faster.
    total = 0
    for i in range(10**9):  # 1 BILLION iterations (10x more!)
        total += i
    
    print("DONE ✅")


# =============================================================================
# REQUIRED: if __name__ == "__main__" GUARD
# =============================================================================
# This is CRITICAL for multiprocessing on Windows!
# Without it, spawning processes causes infinite recursion.

if __name__ == "__main__":
    
    print("=" * 60)
    print("🚀 GIL BYPASS: CPU Work with Multiprocessing (FAST!)")
    print("=" * 60)
    print("Running 2 CPU-heavy tasks in separate processes...")
    print("Watch the TRUE parallelism in action!\n")
    
    start = time.time()
    
    # =========================================================================
    # CREATE 2 PROCESSES
    # =========================================================================
    # Each Process runs in a completely separate Python interpreter
    # with its own GIL - they don't block each other!
    
    processes = [Process(target=cpu_heavy) for _ in range(2)]
    
    # Start all processes (truly parallel on multi-core CPUs!)
    [p.start() for p in processes]
    
    # Wait for all processes to complete
    [p.join() for p in processes]
    
    elapsed = time.time() - start
    print(f"\n⏱️  Time taken: {elapsed:.2f} seconds")
    print("   (Compare with threading - this is MUCH faster for CPU work!)")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🚀 GIL BYPASS: CPU Work with Multiprocessing (FAST!)
# ============================================================
# Running 2 CPU-heavy tasks in separate processes...
# Watch the TRUE parallelism in action!
#
# 🔢 Crunching some numbers...
# 🔢 Crunching some numbers...
#   (both start at the same time!)
#
# DONE ✅
# DONE ✅
#   (both finish at roughly the same time!)
#
# ⏱️  Time taken: 45.00 seconds
#    (Compare with threading - this is MUCH faster for CPU work!)
#
# If this ran sequentially: ~90 seconds
# With multiprocessing: ~45 seconds (2x faster with 2 cores!)
#
# =============================================================================

# =============================================================================
# THREADING VS MULTIPROCESSING FOR CPU WORK
# =============================================================================
#
# ┌─────────────────────┬─────────────────────┬─────────────────────────────┐
# │ Aspect              │ Threading           │ Multiprocessing             │
# ├─────────────────────┼─────────────────────┼─────────────────────────────┤
# │ CPU-bound speedup   │ ❌ None (GIL)       │ ✅ ~N× with N cores         │
# │ Memory              │ Shared              │ Separate (copied)           │
# │ Overhead            │ Low                 │ Higher (process creation)   │
# │ Communication       │ Easy (shared vars)  │ Needs IPC (Queue, Pipe)     │
# │ Best for            │ I/O-bound           │ CPU-bound                   │
# └─────────────────────┴─────────────────────┴─────────────────────────────┘
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Multiprocessing BYPASSES the GIL (each process has its own!)
# 2. TRUE parallel execution on multiple CPU cores
# 3. 2 processes = ~2x faster for CPU-bound work
# 4. Always use if __name__ == "__main__" guard
# 5. Trade-off: higher memory usage, more complex IPC
#
# =============================================================================