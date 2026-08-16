"""
=============================================================================
RUN_IN_EXECUTOR() WITH PROCESSES: CPU-BOUND WORK IN ASYNC
=============================================================================

The Problem:
------------
Sometimes in async code, you need to perform CPU-INTENSIVE operations:
  - Data encryption/decryption
  - Image processing
  - Complex calculations
  - Compression/decompression

CPU-bound work in async code is problematic because:
  1. It doesn't yield to the event loop (no await points)
  2. It blocks the entire event loop, freezing all other coroutines
  3. Even ThreadPoolExecutor won't help much due to the GIL!

The Solution: ProcessPoolExecutor
---------------------------------
Use run_in_executor() with ProcessPoolExecutor instead of ThreadPoolExecutor!

Each process has its OWN Python interpreter and GIL, enabling TRUE parallelism
for CPU-bound work while keeping your async event loop responsive.

ThreadPoolExecutor vs ProcessPoolExecutor:
------------------------------------------
┌─────────────────────────┬───────────────────┬─────────────────────────────┐
│ Aspect                  │ ThreadPoolExecutor│ ProcessPoolExecutor         │
├─────────────────────────┼───────────────────┼─────────────────────────────┤
│ Best for                │ I/O-bound work    │ CPU-bound work              │
│ GIL impact              │ Affected by GIL   │ Bypasses GIL                │
│ Memory                  │ Shared memory     │ Separate memory per process │
│ Overhead                │ Low               │ Higher (process creation)   │
│ Data passing            │ Direct            │ Requires serialization      │
└─────────────────────────┴───────────────────┴─────────────────────────────┘

=============================================================================
"""

import asyncio  # Python's async library
from concurrent.futures import ProcessPoolExecutor  # Process pool for CPU work


def encrypt(data):
    """
    A CPU-BOUND function that simulates encrypting data.
    
    This is a simplified example. Real encryption would involve:
    - Heavy mathematical computations
    - No I/O or network operations
    - Pure CPU work that benefits from true parallelism
    
    Args:
        data (str): The data to encrypt
    
    Returns:
        str: The "encrypted" data (reversed string with lock emoji)
    
    Note:
    -----
    This runs in a SEPARATE PROCESS, so it has:
    - Its own Python interpreter
    - Its own GIL (no blocking other processes!)
    - Its own memory space
    """
    # Simulating CPU-intensive encryption (here just reversing the string)
    # In real scenarios, this could be:
    #   - AES/RSA encryption
    #   - Hashing (bcrypt, scrypt)
    #   - Data transformation algorithms
    
    encrypted = data[::-1]  # Reverse the string (simulated encryption)
    return f"🔒 {encrypted}"


async def main():
    """
    Main async function demonstrating run_in_executor() with ProcessPool.
    """
    print("=" * 60)
    print("🔐 CPU-BOUND ASYNC: ProcessPoolExecutor Demo")
    print("=" * 60)
    print("Running CPU-intensive work in a process pool...\n")
    
    # =========================================================================
    # GET THE RUNNING EVENT LOOP
    # =========================================================================
    
    loop = asyncio.get_running_loop()
    
    # =========================================================================
    # RUN CPU-BOUND CODE IN PROCESS POOL
    # =========================================================================
    #
    # ProcessPoolExecutor creates a pool of worker PROCESSES.
    # Each process has its own Python interpreter and GIL!
    #
    # IMPORTANT DIFFERENCES FROM THREAD POOL:
    # 1. Data is SERIALIZED (pickled) when sent to the process
    # 2. Only picklable objects can be passed as arguments
    # 3. Higher overhead, but true parallelism for CPU work
    
    import time
    start = time.time()
    
    with ProcessPoolExecutor() as pool:
        # Run the CPU-bound encryption in a separate process
        result = await loop.run_in_executor(pool, encrypt, "credit_card_1234")
        print(f"Result: {result}")
    
    end = time.time()
    print(f"\n⏱️  Completed in {end - start:.2f} seconds")


# =============================================================================
# CRITICAL: if __name__ == "__main__" GUARD
# =============================================================================
# This is REQUIRED for multiprocessing on Windows!
# Without it, spawning processes would cause infinite recursion.

if __name__ == "__main__":
    asyncio.run(main())


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🔐 CPU-BOUND ASYNC: ProcessPoolExecutor Demo
# ============================================================
# Running CPU-intensive work in a process pool...
#
# Result: 🔒 4321_drac_tiderc
#
# ⏱️  Completed in 0.15 seconds
#
# =============================================================================

# =============================================================================
# CONCURRENT CPU-BOUND OPERATIONS
# =============================================================================
#
# The real power shows when encrypting multiple items:
#
#     async def main():
#         loop = asyncio.get_running_loop()
#         data_items = ["secret1", "secret2", "secret3", "secret4"]
#         
#         with ProcessPoolExecutor() as pool:
#             tasks = [
#                 loop.run_in_executor(pool, encrypt, item)
#                 for item in data_items
#             ]
#             results = await asyncio.gather(*tasks)
#             
#         for result in results:
#             print(result)
#
# With 4 CPU cores and 4 items:
#   - Sequential: 4 × time
#   - ProcessPool: ~1 × time (true parallelism!)
#
# =============================================================================

# =============================================================================
# CHOOSING THE RIGHT EXECUTOR
# =============================================================================
#
# Use ThreadPoolExecutor when:
#   ✅ Blocking I/O operations (file, network, database)
#   ✅ Calling sync libraries that do I/O
#   ✅ Low overhead is important
#
# Use ProcessPoolExecutor when:
#   ✅ CPU-intensive calculations
#   ✅ Data processing (encryption, compression)
#   ✅ You need to bypass the GIL
#   ✅ True parallelism is required
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. ProcessPoolExecutor runs code in separate PROCESSES
# 2. Each process has its own GIL → true parallelism for CPU work
# 3. Data must be serializable (picklable) to pass between processes
# 4. Higher overhead than threads, but better for CPU-bound tasks
# 5. Always use if __name__ == "__main__" guard!
#
# =============================================================================