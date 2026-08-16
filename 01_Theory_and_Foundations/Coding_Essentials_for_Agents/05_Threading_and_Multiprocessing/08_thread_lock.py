"""
=============================================================================
THREAD LOCKS: THE SOLUTION TO RACE CONDITIONS
=============================================================================

The Problem (from 09_race_condition.py in Asyncio folder):
----------------------------------------------------------
When multiple threads modify shared data, race conditions occur:
  - Operations like `counter += 1` are NOT atomic
  - Threads can interleave, causing lost updates
  - Results are unpredictable!

The Solution: threading.Lock()
------------------------------
A Lock is a synchronization primitive that ensures only ONE thread
can access a "critical section" at a time.

How a Lock Works:
-----------------
    Thread 1: acquire() ─────────────────► [LOCKED]
    Thread 2: acquire() ─── waits... ────►
    Thread 1: release() ─────────────────► [UNLOCKED]
    Thread 2: acquire() ─────────────────► [LOCKED] (now it can proceed)

Visual Timeline:
----------------
WITHOUT LOCK (Race Condition):
    Thread 1: read-modify-write  read-modify-write  read-modify-write
    Thread 2:   read-modify-write  read-modify-write  read-modify-write
              (interleaved = data corruption!)

WITH LOCK:
    Thread 1: [████ locked ████]        [████ locked ████]
    Thread 2:                   [████ locked ████]
              (serialized = correct results!)

This Script:
------------
10 threads, each incrementing a counter 100,000 times.
Expected result: 10 × 100,000 = 1,000,000 ✅
With the lock, we ALWAYS get exactly 1,000,000!

=============================================================================
"""

import threading  # For threads and locks


# =============================================================================
# SHARED STATE AND LOCK
# =============================================================================
# The counter is shared between ALL threads.
# The lock ensures only one thread can modify it at a time.

counter = 0                   # Shared variable (the critical resource)
lock = threading.Lock()       # Lock to protect access to counter


def increment():
    """
    Safely increments the shared counter using a lock.
    
    The `with lock:` statement:
      1. ACQUIRES the lock (blocks if another thread has it)
      2. Executes the critical section (counter += 1)
      3. RELEASES the lock (allows other threads to acquire)
    
    This ensures `counter += 1` is ATOMIC from the perspective
    of other threads - no interleaving can occur!
    """
    global counter  # Access the shared variable
    
    for _ in range(100000):
        # =====================================================================
        # CRITICAL SECTION: Protected by Lock
        # =====================================================================
        # 
        # `with lock:` is equivalent to:
        #     lock.acquire()      # Wait for lock, then take it
        #     try:
        #         counter += 1    # Critical section
        #     finally:
        #         lock.release()  # Always release, even if exception
        #
        # The context manager (`with`) is cleaner and safer!
        
        with lock:
            counter += 1
            # Only ONE thread can be inside this block at a time!
            # Other threads wait at `with lock:` until it's released.


# =============================================================================
# CREATE AND RUN 10 THREADS
# =============================================================================

print("=" * 50)
print("🔒 THREAD LOCK DEMONSTRATION")
print("=" * 50)
print("10 threads, each incrementing 100,000 times")
print("Expected result: 1,000,000")
print("-" * 50 + "\n")

# Create 10 threads
threads = [threading.Thread(target=increment) for _ in range(10)]

# Start all threads
# Note: List comprehension for side effects (not Pythonic, but compact)
[t.start() for t in threads]

# Wait for all threads to complete
[t.join() for t in threads]


# =============================================================================
# VERIFY THE RESULT
# =============================================================================

print(f"📊 Final counter: {counter}")
print(f"   Expected:      1000000")

if counter == 1000000:
    print("\n✅ SUCCESS! Lock prevented race condition!")
else:
    print(f"\n❌ ERROR! Lost {1000000 - counter} increments")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ==================================================
# 🔒 THREAD LOCK DEMONSTRATION
# ==================================================
# 10 threads, each incrementing 100,000 times
# Expected result: 1,000,000
# --------------------------------------------------
#
# 📊 Final counter: 1000000
#    Expected:      1000000
#
# ✅ SUCCESS! Lock prevented race condition!
#
# Compare with race condition example (no lock) where result is random!
#
# =============================================================================

# =============================================================================
# TRADE-OFF: CORRECTNESS vs PERFORMANCE
# =============================================================================
#
# Locks ensure CORRECTNESS but reduce PARALLELISM:
#
# Without lock: Fast but WRONG results (race condition)
# With lock:    Slower but CORRECT results
#
# The lock serializes access to the critical section, meaning threads
# execute that section one at a time. This is necessary for correctness!
#
# For better performance with shared counters, consider:
#   - threading.RLock() - Reentrant lock (same thread can acquire twice)
#   - queue.Queue() - Thread-safe queue (no explicit locking needed)
#   - collections.Counter with lock
#   - Reduce lock scope (lock only what's necessary)
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Lock ensures only ONE thread accesses critical section at a time
# 2. Use `with lock:` for automatic acquire/release (safer!)
# 3. Locks prevent race conditions but reduce parallelism
# 4. Always lock the MINIMUM necessary code (reduce contention)
# 5. Result is now deterministic: always 1,000,000!
#
# =============================================================================