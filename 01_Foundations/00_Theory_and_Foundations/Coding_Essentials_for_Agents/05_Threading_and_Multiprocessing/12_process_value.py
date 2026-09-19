"""
=============================================================================
SHARED MEMORY BETWEEN PROCESSES: VALUE
=============================================================================

The Problem:
------------
Processes have SEPARATE memory spaces. But sometimes you need to share
a simple value (like a counter) between processes.

The Solution: multiprocessing.Value
------------------------------------
Value creates a SHARED MEMORY object that can be accessed by multiple
processes. It's like a single variable that exists in shared memory!

How Value Works:
----------------
    ┌─────────────────┐                      ┌─────────────────┐
    │    Process 1    │                      │    Process 2    │
    │                 │                      │                 │
    │  counter.value  │◄───────┐  ┌─────────►│  counter.value  │
    │                 │        │  │          │                 │
    └─────────────────┘        │  │          └─────────────────┘
                               │  │
                        ┌──────┴──┴──────┐
                        │ SHARED MEMORY  │
                        │ ┌────────────┐ │
                        │ │ Value = 42 │ │
                        │ └────────────┘ │
                        └────────────────┘
    
    Both processes access the SAME memory location!

IMPORTANT: Value and Locking
----------------------------
Just like threads, processes accessing shared memory can have RACE CONDITIONS!
Value has a built-in lock: counter.get_lock()

Value Types:
------------
Value('i', 0)  → Signed integer (initialized to 0)
Value('d', 0.0) → Double (float)
Value('c', b'x') → Character
Value('b', 0)  → Signed char

The first argument is a TYPE CODE (from the `array` module).

=============================================================================
"""

from multiprocessing import Process, Value  # Process and shared Value


def increment(counter):
    """
    Increments a shared counter 100,000 times.
    
    Args:
        counter (Value): A multiprocessing Value object (shared memory)
    
    IMPORTANT: We use counter.get_lock() to prevent race conditions!
    Without the lock, processes would interleave their read-modify-write
    operations, causing lost updates (just like with threads!).
    """
    for _ in range(100000):
        # =====================================================================
        # CRITICAL SECTION: Protected by Value's Built-in Lock
        # =====================================================================
        #
        # counter.get_lock() returns the lock associated with this Value
        # Using `with` ensures proper acquire/release
        #
        # Without this lock:
        #   - Processes would read-modify-write simultaneously
        #   - Updates would be lost (race condition!)
        #   - Final count would be LESS than expected
        #
        # With this lock:
        #   - Only one process modifies at a time
        #   - All updates are counted
        #   - Final count is EXACTLY as expected!
        
        with counter.get_lock():
            counter.value += 1


# =============================================================================
# REQUIRED: if __name__ == "__main__" GUARD
# =============================================================================

if __name__ == "__main__":
    
    print("=" * 60)
    print("🔗 SHARED MEMORY: Value Demo with Locking")
    print("=" * 60)
    print("4 processes, each incrementing shared counter 100,000 times")
    print("Expected result: 400,000")
    print("-" * 60 + "\n")
    
    # =========================================================================
    # CREATE SHARED VALUE
    # =========================================================================
    # Value('i', 0) creates:
    #   - 'i' = signed integer type
    #   - 0 = initial value
    #
    # This value exists in SHARED MEMORY accessible by all processes!
    
    counter = Value('i', 0)  # Shared integer initialized to 0
    
    # =========================================================================
    # CREATE AND RUN 4 PROCESSES
    # =========================================================================
    # All processes receive the SAME counter object (shared memory reference)
    
    processes = [Process(target=increment, args=(counter,)) for _ in range(4)]
    
    # Start all processes
    [p.start() for p in processes]
    
    # Wait for all to complete
    [p.join() for p in processes]
    
    # =========================================================================
    # VERIFY THE RESULT
    # =========================================================================
    
    print(f"📊 Final counter value: {counter.value}")
    print(f"   Expected:            400000")
    
    if counter.value == 400000:
        print("\n✅ SUCCESS! Lock prevented race condition across processes!")
    else:
        print(f"\n❌ ERROR! Lost {400000 - counter.value} increments")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🔗 SHARED MEMORY: Value Demo with Locking
# ============================================================
# 4 processes, each incrementing shared counter 100,000 times
# Expected result: 400,000
# ------------------------------------------------------------
#
# 📊 Final counter value: 400000
#    Expected:            400000
#
# ✅ SUCCESS! Lock prevented race condition across processes!
#
# =============================================================================

# =============================================================================
# VALUE vs QUEUE: WHEN TO USE WHICH?
# =============================================================================
#
# ┌─────────────────────┬─────────────────────┬─────────────────────────────┐
# │ Feature             │ Value               │ Queue                       │
# ├─────────────────────┼─────────────────────┼─────────────────────────────┤
# │ Data type           │ Single value        │ Multiple items              │
# │ Access pattern      │ Read/write          │ Put/get (FIFO)              │
# │ Use case            │ Shared counter      │ Message passing             │
# │ Locking             │ Built-in lock       │ Automatic (thread-safe)     │
# │ Size                │ Fixed (one value)   │ Variable                    │
# └─────────────────────┴─────────────────────┴─────────────────────────────┘
#
# Use Value when: You need a shared counter, flag, or simple variable
# Use Queue when: You need to pass multiple messages between processes
#
# =============================================================================

# =============================================================================
# MULTIPROCESSING.ARRAY: SHARED ARRAYS
# =============================================================================
#
# For sharing multiple values, use Array:
#
#     from multiprocessing import Array
#     
#     # Create shared array of 10 integers, all initialized to 0
#     arr = Array('i', [0] * 10)
#     
#     # Access elements
#     arr[0] = 42
#     print(arr[0])
#     
#     # Lock the entire array
#     with arr.get_lock():
#         arr[0] += 1
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Value creates a SHARED MEMORY variable across processes
# 2. Type codes: 'i' (int), 'd' (double), 'c' (char), 'b' (byte)
# 3. ALWAYS use get_lock() to prevent race conditions!
# 4. Value is simpler than Queue for single shared values
# 5. Result is deterministic when properly locked
#
# =============================================================================