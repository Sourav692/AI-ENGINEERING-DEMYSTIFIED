"""
=============================================================================
INTRODUCTION TO ASYNCIO: ASYNCHRONOUS PROGRAMMING IN PYTHON
=============================================================================

What is Asyncio?
----------------
Asyncio is Python's built-in library for writing ASYNCHRONOUS code using
the async/await syntax. It allows you to write concurrent code that runs
in a SINGLE THREAD!

Threading vs Asyncio:
---------------------
┌─────────────────────┬──────────────────────────────────────────────────────┐
│ Threading           │ Asyncio                                              │
├─────────────────────┼──────────────────────────────────────────────────────┤
│ Multiple threads    │ Single thread                                        │
│ OS manages switching│ YOU control when to switch (await)                   │
│ Preemptive          │ Cooperative                                          │
│ Higher memory usage │ Lower memory usage                                   │
│ Good for blocking IO│ Best for non-blocking async I/O                      │
│ Race conditions risk│ Fewer race conditions                                │
└─────────────────────┴──────────────────────────────────────────────────────┘

Key Concepts:
-------------
1. COROUTINE: A function defined with `async def` (can be paused/resumed)
2. AWAIT: Pauses the coroutine until the awaited task completes
3. EVENT LOOP: The engine that runs and manages all coroutines

How Asyncio Works (Visual):
---------------------------
Traditional (blocking):
    Task 1: ████████████████████  (running/waiting)
    Task 2:                      ████████████████████
            ← Task 2 waits for Task 1 to COMPLETELY finish →

Asyncio (cooperative):
    Task 1: ████░░░░░░░░░░░░████  (runs, awaits, runs again)
    Task 2:     ████░░░░░░░░████  (runs during Task 1's await)
            ← Single thread, tasks take turns at await points →

When to Use Asyncio:
--------------------
✅ Network operations (HTTP requests, websockets)
✅ Database queries (async DB drivers)
✅ File I/O (with async libraries)
✅ When you need many concurrent I/O operations
❌ NOT for CPU-bound tasks (use multiprocessing instead)

=============================================================================
"""

import asyncio  # Python's built-in async library (available since Python 3.4)


# =============================================================================
# DEFINING A COROUTINE WITH async def
# =============================================================================
# 
# async def creates a COROUTINE FUNCTION (not a regular function!)
# 
# Key differences from regular functions:
#   - Regular function: def foo() → returns a value immediately
#   - Coroutine function: async def foo() → returns a coroutine object
#   - Coroutine must be "awaited" or "run" to execute

async def brew_chai():
    """
    A simple coroutine that simulates brewing chai.
    
    This is our first async function! Notice:
    1. Defined with `async def` instead of just `def`
    2. Uses `await` to pause execution (non-blocking wait)
    3. Must be run with asyncio.run() or awaited by another coroutine
    """
    print("☕ Brewing chai...")
    
    # =========================================================================
    # AWAIT: The Heart of Async Programming
    # =========================================================================
    # 
    # `await` does two things:
    #   1. PAUSES this coroutine (gives control back to event loop)
    #   2. WAITS for the awaited operation to complete
    #
    # During this pause, OTHER coroutines can run!
    # This is how we achieve concurrency in a single thread.
    #
    # IMPORTANT: asyncio.sleep() vs time.sleep()
    # ───────────────────────────────────────────
    # time.sleep(2)      → BLOCKS the entire thread (bad for async!)
    # asyncio.sleep(2)   → YIELDS control, lets other tasks run (good!)
    
    await asyncio.sleep(2)  # Non-blocking wait for 2 seconds
    
    print("✅ Chai is ready!")


# =============================================================================
# RUNNING A COROUTINE WITH asyncio.run()
# =============================================================================
#
# You CANNOT call a coroutine like a regular function:
#   brew_chai()  ← This returns a coroutine object, NOT the result!
#
# You MUST run it using one of these methods:
#   1. asyncio.run(coroutine)    ← Entry point for async programs
#   2. await coroutine           ← From inside another coroutine
#   3. asyncio.create_task()     ← Schedule for concurrent execution
#
# asyncio.run() does the following:
#   1. Creates a new EVENT LOOP
#   2. Runs the coroutine until completion
#   3. Closes the event loop
#   4. Returns the coroutine's result

print("=" * 50)
print("🚀 ASYNCIO BASICS: Your First Coroutine")
print("=" * 50 + "\n")

asyncio.run(brew_chai())

# async def main():
#     await brew_chai()

# asyncio.run(main())

print("\n🎉 Async program completed!")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ==================================================
# 🚀 ASYNCIO BASICS: Your First Coroutine
# ==================================================
#
# ☕ Brewing chai...
# (2 second pause)
# ✅ Chai is ready!
#
# 🎉 Async program completed!
#
# =============================================================================

# =============================================================================
# WHY THIS EXAMPLE SEEMS SIMPLE
# =============================================================================
#
# This example has only ONE coroutine, so you won't see the benefit yet.
# The power of asyncio shows when you have MULTIPLE coroutines:
#
#     async def main():
#         await asyncio.gather(
#             brew_chai(),      # These all run
#             brew_chai(),      # concurrently in
#             brew_chai(),      # a single thread!
#         )
#
# With 3 chai brewings of 2 seconds each:
#   - Sequential: 6 seconds
#   - Async (gather): ~2 seconds!
#
# See the next examples for multi-coroutine demonstrations!
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. `async def` defines a COROUTINE (a pausable function)
# 2. `await` PAUSES the coroutine and yields control to the event loop
# 3. `asyncio.run()` is the ENTRY POINT for running async code
# 4. `asyncio.sleep()` is non-blocking; `time.sleep()` is blocking
# 5. The benefit appears when running MULTIPLE coroutines concurrently
#
# The async/await model:
#   - Single thread (no GIL issues!)
#   - Cooperative multitasking (you decide when to yield with await)
#   - Perfect for I/O-bound concurrent operations
#   - Lower memory overhead than threading
#
# =============================================================================

# =============================================================================
# COMMON MISTAKES TO AVOID
# =============================================================================
#
# ❌ WRONG: Calling coroutine without await or run
#     brew_chai()  # Returns coroutine object, doesn't execute!
#
# ❌ WRONG: Using time.sleep() in async code
#     await time.sleep(2)  # time.sleep is not awaitable!
#
# ❌ WRONG: Using await outside of async function
#     await brew_chai()  # SyntaxError! Must be inside async def
#
# ✅ CORRECT: Use asyncio.run() at the top level
#     asyncio.run(brew_chai())
#
# ✅ CORRECT: Use await inside async functions
#     async def main():
#         await brew_chai()
#
# =============================================================================