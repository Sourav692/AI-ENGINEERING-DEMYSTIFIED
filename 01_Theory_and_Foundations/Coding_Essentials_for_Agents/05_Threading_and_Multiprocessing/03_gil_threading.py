"""
=============================================================================
THE GLOBAL INTERPRETER LOCK (GIL) - THREADING'S ACHILLES HEEL
=============================================================================

What is the GIL?
----------------
The Global Interpreter Lock (GIL) is a mutex (lock) in CPython that allows
only ONE thread to execute Python bytecode at a time, even on multi-core CPUs.

Why does Python have a GIL?
---------------------------
1. Memory Management: Python uses reference counting for garbage collection.
   The GIL prevents race conditions when multiple threads modify ref counts.
2. Simplicity: Makes the CPython interpreter simpler and thread-safe.
3. C Extensions: Many C libraries aren't thread-safe; GIL protects them.

How the GIL Works:
------------------
    Thread 1: ████████░░░░░░░░████████░░░░░░░░████████
    Thread 2: ░░░░░░░░████████░░░░░░░░████████░░░░░░░░
              ^       ^       ^       ^       ^
              |       |       |       |       |
              GIL switches between threads every ~5ms (Python 3.2+)

Even with 2 threads, only ONE executes Python code at any moment!

The GIL's Impact:
-----------------
┌─────────────────────┬─────────────────────────────────────────────────────┐
│ Task Type           │ GIL Impact                                          │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ I/O-bound           │ MINIMAL - GIL is released during I/O operations    │
│ (file, network)     │ Threading works well! ✅                            │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ CPU-bound           │ SEVERE - Only one thread runs at a time            │
│ (calculations)      │ Threading provides NO speedup! ❌                   │
└─────────────────────┴─────────────────────────────────────────────────────┘

This Script Demonstrates:
-------------------------
A CPU-bound task (counting to 100 million) running in 2 threads.
You'll see that 2 threads take LONGER than you'd expect because:
1. Only one thread runs at a time (GIL)
2. Extra overhead from thread switching and GIL acquisition/release

Expected Result: ~Same time (or WORSE) than running sequentially!

=============================================================================
"""

import threading  # Python's threading module
import time       # For measuring execution time


def brew_chai():
    """
    A CPU-BOUND task that demonstrates GIL limitations.
    
    This function performs pure computation (counting) with no I/O.
    During this entire function, the thread HOLDS the GIL, preventing
    other threads from executing Python bytecode.
    
    Note: threading.current_thread().name returns the thread's name,
    useful for identifying which thread is running.
    """
    print(f"🔄 {threading.current_thread().name} started brewing...")
    
    # =========================================================================
    # CPU-BOUND WORK: Pure computation, no I/O
    # =========================================================================
    # This loop performs 100 million increments.
    # The underscore (_) is a convention for "unused loop variable"
    # 100_000_000 uses Python's numeric literal separator for readability
    
    count = 0
    for _ in range(100_000_000):  # 100 million iterations!
        count += 1
        # During this loop, this thread holds the GIL
        # Other threads are BLOCKED from running Python code!
        # (GIL is briefly released every ~5ms for thread switching)
    
    print(f"✅ {threading.current_thread().name} finished brewing...")


# =============================================================================
# CREATING NAMED THREADS
# =============================================================================
# The 'name' parameter helps identify threads in output and debugging
# Without it, threads get names like "Thread-1", "Thread-2"

thread1 = threading.Thread(target=brew_chai, name="Barista-1")
thread2 = threading.Thread(target=brew_chai, name="Barista-2")


# =============================================================================
# TIMING THE EXECUTION
# =============================================================================
# We measure total time to show that threading doesn't help CPU-bound tasks

print("=" * 60)
print("🧪 GIL DEMONSTRATION: CPU-bound task with Threading")
print("=" * 60)
print(f"Running 2 threads, each counting to 100 million...\n")

start = time.time()

# Start both threads (they'll run "concurrently" but not in parallel)
thread1.start()
thread2.start()

# Wait for both to complete
thread1.join()
thread2.join()

end = time.time()

print(f"\n⏱️  Total time taken: {end - start:.2f} seconds")


# =============================================================================
# UNDERSTANDING THE RESULTS
# =============================================================================
# 
# EXPECTED BEHAVIOR:
# ------------------
# If threading truly parallelized work:
#   - Single thread: ~X seconds
#   - Two threads: ~X/2 seconds (half the time)
#
# ACTUAL BEHAVIOR (due to GIL):
# -----------------------------
#   - Single thread: ~X seconds
#   - Two threads: ~X seconds OR EVEN LONGER!
#
# Why longer? Because of:
#   1. GIL acquisition/release overhead
#   2. Thread context switching overhead
#   3. Cache thrashing between threads
#
# =============================================================================

# =============================================================================
# VISUAL TIMELINE OF WHAT HAPPENS
# =============================================================================
#
# What you might EXPECT (true parallelism):
# ─────────────────────────────────────────
# Barista-1: ████████████████████████████████ (counting 0-100M)
# Barista-2: ████████████████████████████████ (counting 0-100M)
#            |←─────── ~X seconds ─────────→|
#
# What ACTUALLY happens (GIL switching):
# ──────────────────────────────────────
# Barista-1: ████░░░░████░░░░████░░░░████░░░░████░░░░████░░░░
# Barista-2: ░░░░████░░░░████░░░░████░░░░████░░░░████░░░░████
#            |←─────────────── ~2X seconds ──────────────→|
#            ↑    ↑    ↑    ↑
#            GIL switches every ~5ms (costly for CPU work!)
#
# =============================================================================

# =============================================================================
# THE SOLUTION: USE MULTIPROCESSING FOR CPU-BOUND TASKS
# =============================================================================
# See 04_gil_multiprocessing.py for the solution!
# Multiprocessing creates separate processes, each with its OWN GIL,
# enabling TRUE parallel execution on multiple CPU cores.
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
# 1. GIL = Only one thread executes Python bytecode at a time
# 2. Threading is GREAT for I/O-bound tasks (waiting for files, network)
# 3. Threading is BAD for CPU-bound tasks (pure computation)
# 4. Use multiprocessing for CPU-bound parallel work
# 5. The GIL is a CPython implementation detail (PyPy, Jython don't have it)
# =============================================================================