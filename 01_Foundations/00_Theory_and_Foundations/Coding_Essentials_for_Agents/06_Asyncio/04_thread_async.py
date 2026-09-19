"""
=============================================================================
BRIDGING SYNC AND ASYNC: run_in_executor() WITH THREADS
=============================================================================

The Problem:
------------
You're writing async code, but you need to use a library that is SYNCHRONOUS
(blocking). Examples:
  - Database drivers without async support
  - File operations (some)
  - Third-party libraries that use time.sleep() or blocking I/O
  - CPU-bound operations

If you call blocking code directly in async, it BLOCKS the entire event loop!

The Solution: run_in_executor()
-------------------------------
run_in_executor() runs blocking code in a SEPARATE THREAD (or process),
allowing your async event loop to continue processing other coroutines!

How It Works:
-------------
    ┌──────────────────────────────────────────────────────────────────────┐
    │  Main Thread (Event Loop)                                            │
    │  ┌────────────────────────────────────────────────────────────────┐  │
    │  │ async def main():                                              │  │
    │  │     result = await loop.run_in_executor(pool, blocking_func)   │  │
    │  │                         │                                      │  │
    │  │                         ▼                                      │  │
    │  │     ┌─────────── runs in ───────────┐                          │  │
    │  │     │  ThreadPoolExecutor           │                          │  │
    │  │     │  ┌─────────────────────────┐  │                          │  │
    │  │     │  │ blocking_func()         │  │ ← Runs in separate       │  │
    │  │     │  │ time.sleep(3)           │  │   thread, doesn't        │  │
    │  │     │  │ return result           │  │   block event loop!      │  │
    │  │     │  └─────────────────────────┘  │                          │  │
    │  │     └───────────────────────────────┘                          │  │
    │  └────────────────────────────────────────────────────────────────┘  │
    └──────────────────────────────────────────────────────────────────────┘

When to Use:
------------
✅ I/O-bound blocking operations (file I/O, sync database calls)
✅ Third-party sync libraries you can't change
✅ Legacy code integration
❌ NOT ideal for CPU-bound work (use ProcessPoolExecutor instead)

=============================================================================
"""

import asyncio                              # Python's async library
import time                                 # For simulating blocking work
from concurrent.futures import ThreadPoolExecutor  # Thread pool for blocking work


def check_stock(item):
    """
    A SYNCHRONOUS (blocking) function that simulates checking inventory.
    
    This function uses time.sleep() which is BLOCKING - it would freeze
    the entire event loop if called directly from async code!
    
    By running it in an executor, we offload it to a separate thread.
    
    Args:
        item (str): The item to check stock for
    
    Returns:
        str: Stock information for the item
    """
    print(f"📦 Checking {item} in store...")
    
    # This is a BLOCKING operation!
    # If called directly in async code, it would block the event loop.
    # run_in_executor() solves this by running it in a separate thread.
    time.sleep(3)  # Simulates database query or API call
    
    return f"✅ {item} stock: 42 units available"


async def main():
    """
    Main async function demonstrating run_in_executor() with ThreadPool.
    """
    print("=" * 60)
    print("🔄 BRIDGING SYNC & ASYNC: run_in_executor() Demo")
    print("=" * 60)
    print("Running blocking function in a thread pool...\n")
    
    # =========================================================================
    # GET THE RUNNING EVENT LOOP
    # =========================================================================
    # We need a reference to the event loop to use run_in_executor()
    
    loop = asyncio.get_running_loop()
    
    # =========================================================================
    # RUN BLOCKING CODE IN THREAD POOL
    # =========================================================================
    #
    # ThreadPoolExecutor creates a pool of worker threads.
    # run_in_executor() submits our blocking function to this pool.
    #
    # Syntax:
    #   loop.run_in_executor(executor, func, *args)
    #
    # Parameters:
    #   - executor: ThreadPoolExecutor (or None for default)
    #   - func: The blocking function to run
    #   - *args: Arguments to pass to the function
    #
    # Returns: A Future that can be awaited
    
    start = time.time()
    
    with ThreadPoolExecutor() as pool:
        # await makes this non-blocking from the event loop's perspective!
        # The blocking call runs in a separate thread.
        result = await loop.run_in_executor(pool, check_stock, "Masala chai")
        print(result)
    
    end = time.time()
    print(f"\n⏱️  Completed in {end - start:.2f} seconds")


# Run the async main function
asyncio.run(main())


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🔄 BRIDGING SYNC & ASYNC: run_in_executor() Demo
# ============================================================
# Running blocking function in a thread pool...
#
# 📦 Checking Masala chai in store...
# (3 second pause)
# ✅ Masala chai stock: 42 units available
#
# ⏱️  Completed in 3.00 seconds
#
# =============================================================================

# =============================================================================
# RUNNING MULTIPLE BLOCKING CALLS CONCURRENTLY
# =============================================================================
#
# The real power shows when running multiple blocking calls:
#
#     async def main():
#         loop = asyncio.get_running_loop()
#         with ThreadPoolExecutor() as pool:
#             # Run 3 blocking calls concurrently!
#             results = await asyncio.gather(
#                 loop.run_in_executor(pool, check_stock, "Masala"),
#                 loop.run_in_executor(pool, check_stock, "Ginger"),
#                 loop.run_in_executor(pool, check_stock, "Green"),
#             )
#             for result in results:
#                 print(result)
#
# 3 calls × 3 seconds each:
#   - Sequential: 9 seconds
#   - With executor + gather: ~3 seconds!
#
# =============================================================================

# =============================================================================
# USING DEFAULT EXECUTOR (SIMPLER SYNTAX)
# =============================================================================
#
# You can pass None as the executor to use the default thread pool:
#
#     result = await loop.run_in_executor(None, blocking_func, arg1, arg2)
#
# This is simpler but gives you less control over the pool size.
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. run_in_executor() bridges sync (blocking) and async code
# 2. ThreadPoolExecutor runs blocking code in separate threads
# 3. The event loop remains responsive while blocking code executes
# 4. Use with asyncio.gather() for concurrent blocking operations
# 5. Great for integrating legacy sync libraries into async code
#
# =============================================================================