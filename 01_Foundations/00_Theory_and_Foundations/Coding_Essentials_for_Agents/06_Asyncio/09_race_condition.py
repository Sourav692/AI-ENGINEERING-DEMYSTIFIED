"""
=============================================================================
RACE CONDITIONS: THE HIDDEN DANGER OF SHARED STATE
=============================================================================

What is a Race Condition?
-------------------------
A RACE CONDITION occurs when two or more threads access SHARED DATA
simultaneously, and at least one thread MODIFIES it.

The result? UNPREDICTABLE BEHAVIOR!

The Problem in This Script:
---------------------------
Two threads both increment `chai_stock` 100,000 times each.
Expected result: 200,000 (100,000 × 2)
Actual result: Usually LESS than 200,000! 😱

Why Does This Happen?
---------------------
The operation `chai_stock += 1` is NOT ATOMIC (not a single operation).
It actually consists of THREE steps:

    1. READ:  temp = chai_stock      (read current value)
    2. ADD:   temp = temp + 1        (add 1)
    3. WRITE: chai_stock = temp      (write back)

When two threads interleave these steps, data is LOST:

    Thread A              Thread B              chai_stock
    ──────────────────    ──────────────────    ──────────────
    read (gets 100)                             100
                          read (gets 100)       100
    add (100 + 1)                               100
                          add (100 + 1)         100
    write (101)                                 101
                          write (101)           101  ← Should be 102!

Both threads read 100, both add 1, both write 101.
We LOST one increment! This happens thousands of times.

=============================================================================
"""

import threading  # For creating threads


# =============================================================================
# SHARED STATE: THE SOURCE OF THE PROBLEM
# =============================================================================
# This variable is shared between ALL threads.
# Multiple threads reading AND writing = DANGER!

chai_stock = 0


def restock():
    """
    Increments the shared chai_stock counter 100,000 times.
    
    This function demonstrates a RACE CONDITION:
    - Uses `global` to access shared variable
    - The += operation is NOT thread-safe
    - Results will be unpredictable when run in multiple threads
    
    THE PROBLEM:
    chai_stock += 1 is actually THREE operations:
        1. READ the current value
        2. ADD 1 to it
        3. WRITE the new value back
    
    Threads can interleave between these steps, causing lost updates!
    """
    global chai_stock  # Access the shared variable
    
    for _ in range(100000):
        # THIS IS NOT THREAD-SAFE!
        # Another thread can read/modify chai_stock between
        # our read and write operations!
        chai_stock += 1


# =============================================================================
# CREATE AND RUN TWO THREADS
# =============================================================================

print("=" * 50)
print("⚠️  RACE CONDITION DEMONSTRATION")
print("=" * 50)
print("Two threads, each incrementing 100,000 times")
print("Expected result: 200,000")
print("-" * 50)

# Create 2 threads that both modify the same shared variable
threads = [threading.Thread(target=restock) for _ in range(2)]

# Start all threads
for t in threads:
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

# =============================================================================
# CHECK THE RESULT
# =============================================================================

print(f"\n📊 Final chai stock: {chai_stock}")
print(f"   Expected:         200000")
print(f"   Lost increments:  {200000 - chai_stock}")

if chai_stock < 200000:
    print("\n❌ RACE CONDITION DETECTED!")
    print("   Some increments were lost due to concurrent access.")
else:
    print("\n✅ Got lucky this time! (Race condition may still exist)")


# =============================================================================
# EXPECTED OUTPUT (values vary each run!)
# =============================================================================
#
# ==================================================
# ⚠️  RACE CONDITION DEMONSTRATION
# ==================================================
# Two threads, each incrementing 100,000 times
# Expected result: 200,000
# --------------------------------------------------
#
# 📊 Final chai stock: 156432    ← Different every run!
#    Expected:         200000
#    Lost increments:  43568
#
# ❌ RACE CONDITION DETECTED!
#    Some increments were lost due to concurrent access.
#
# =============================================================================

# =============================================================================
# THE FIX: USE A LOCK
# =============================================================================
#
# A Lock ensures only ONE thread can access the critical section at a time:
#
#     lock = threading.Lock()
#     
#     def restock_safe():
#         global chai_stock
#         for _ in range(100000):
#             with lock:  # Only one thread at a time!
#                 chai_stock += 1
#
# See 08_thread_lock.py in the threading folder for the complete solution!
#
# =============================================================================

# =============================================================================
# OTHER SOLUTIONS
# =============================================================================
#
# 1. threading.Lock() - Manual locking (shown above)
# 2. queue.Queue() - Thread-safe queue for producer/consumer patterns
# 3. threading.RLock() - Reentrant lock (can be acquired multiple times)
# 4. threading.Condition() - For complex synchronization
# 5. Atomic operations - Using libraries like `atomics`
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Race conditions occur with shared mutable state + multiple threads
# 2. Operations like += are NOT atomic (read-modify-write)
# 3. Results are unpredictable and vary between runs
# 4. Use locks to protect critical sections
# 5. Avoid shared mutable state when possible!
#
# =============================================================================