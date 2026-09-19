"""
=============================================================================
ASYNCIO.GATHER(): RUNNING MULTIPLE COROUTINES CONCURRENTLY
=============================================================================

The Power of asyncio.gather()
-----------------------------
In the previous example, we ran a single coroutine. But the real power of
asyncio comes when running MULTIPLE coroutines CONCURRENTLY!

asyncio.gather() takes multiple coroutines and runs them ALL at the same time,
waiting for ALL to complete before returning.

How It Works:
-------------
    await asyncio.gather(
        coroutine1(),
        coroutine2(),
        coroutine3(),
    )

All three coroutines start immediately and run concurrently.
gather() returns when ALL coroutines have completed.

Time Comparison:
----------------
SEQUENTIAL (one after another):
    brew("Masala")  → 3 seconds
    brew("Green")   → 3 seconds  
    brew("Ginger")  → 3 seconds
    Total: 9 seconds ❌

CONCURRENT (with asyncio.gather):
    brew("Masala")  ─┬─ All run
    brew("Green")   ─┼─ at the
    brew("Ginger")  ─┘─ same time!
    Total: ~3 seconds ✅ (time of the longest task)

This is 3x faster! And all in a SINGLE THREAD!

=============================================================================
"""

import asyncio  # Python's async library
import time     # Imported but commented out - see note below


async def brew(name):
    """
    Simulates brewing a specific type of chai.
    
    Each brew takes 3 seconds, but when run concurrently with gather(),
    multiple brews happen at the same time!
    
    Args:
        name (str): The type of chai being brewed
    """
    print(f"☕ Brewing {name}...")
    
    # =========================================================================
    # ASYNC SLEEP vs REGULAR SLEEP - CRITICAL DIFFERENCE!
    # =========================================================================
    # 
    # ✅ asyncio.sleep(3) - NON-BLOCKING
    #    - Yields control to the event loop
    #    - Other coroutines can run during this time
    #    - This is what enables concurrency!
    #
    # ❌ time.sleep(3) - BLOCKING (commented out below)
    #    - Blocks the ENTIRE event loop
    #    - NO other coroutines can run
    #    - Defeats the purpose of async!
    #
    # Try uncommenting time.sleep(3) and commenting asyncio.sleep(3)
    # to see the difference: total time will be 9 seconds instead of 3!
    
    await asyncio.sleep(3)  # Non-blocking: other coroutines run during this
    # time.sleep(3)         # Blocking: would make this take 9 seconds total!
    
    print(f"✅ {name} is ready!")


async def main():
    """
    Main coroutine that brews 3 types of chai concurrently.
    
    asyncio.gather() is the KEY to running multiple coroutines at once!
    """
    print("=" * 50)
    print("🫖 CHAI SHOP: Concurrent Brewing with gather()")
    print("=" * 50)
    print("Brewing 3 types of chai concurrently...\n")
    
    start = time.time()
    
    # =========================================================================
    # ASYNCIO.GATHER() - Run Multiple Coroutines Concurrently
    # =========================================================================
    #
    # Syntax: await asyncio.gather(coro1, coro2, coro3, ...)
    #
    # What it does:
    #   1. Starts ALL coroutines immediately
    #   2. Runs them concurrently (switching at await points)
    #   3. Waits for ALL to complete
    #   4. Returns a list of results (in order of input)
    #
    # Note: We pass coroutine CALLS (with parentheses), not the functions!
    
    await asyncio.gather(
        brew("Masala chai"),   # Starts immediately
        brew("Green chai"),    # Starts immediately (concurrent!)
        brew("Ginger chai"),   # Starts immediately (concurrent!)
    )
    
    end = time.time()
    print(f"\n🎉 All chai ready in {end - start:.2f} seconds!")
    print("   (3 brews × 3 seconds each, but only ~3 seconds total!)")


# Run the main coroutine
asyncio.run(main())


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ==================================================
# 🫖 CHAI SHOP: Concurrent Brewing with gather()
# ==================================================
# Brewing 3 types of chai concurrently...
#
# ☕ Brewing Masala chai...
# ☕ Brewing Green chai...
# ☕ Brewing Ginger chai...
#   (all 3 start almost instantly!)
#
# ✅ Masala chai is ready!
# ✅ Green chai is ready!
# ✅ Ginger chai is ready!
#   (all 3 finish at roughly the same time, ~3 seconds later)
#
# 🎉 All chai ready in 3.00 seconds!
#    (3 brews × 3 seconds each, but only ~3 seconds total!)
#
# =============================================================================

# =============================================================================
# GATHER() RETURN VALUES
# =============================================================================
#
# If your coroutines return values, gather() collects them:
#
#     async def fetch_data(id):
#         await asyncio.sleep(1)
#         return f"Data for {id}"
#
#     async def main():
#         results = await asyncio.gather(
#             fetch_data(1),
#             fetch_data(2),
#             fetch_data(3),
#         )
#         print(results)  # ['Data for 1', 'Data for 2', 'Data for 3']
#
# Results are returned in the SAME ORDER as the input coroutines,
# regardless of which one finishes first!
#
# =============================================================================

# =============================================================================
# ALTERNATIVES TO GATHER()
# =============================================================================
#
# 1. asyncio.create_task() - For more control over individual tasks
#
#     task1 = asyncio.create_task(brew("Masala"))
#     task2 = asyncio.create_task(brew("Green"))
#     await task1
#     await task2
#
# 2. asyncio.wait() - When you need to handle completions as they happen
#
#     tasks = [asyncio.create_task(brew(name)) for name in names]
#     done, pending = await asyncio.wait(tasks)
#
# 3. asyncio.as_completed() - Process results as they complete
#
#     for coro in asyncio.as_completed([brew("A"), brew("B")]):
#         result = await coro
#         print(f"Completed: {result}")
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. asyncio.gather() runs multiple coroutines CONCURRENTLY
# 2. Total time = time of the LONGEST coroutine (not sum of all)
# 3. All coroutines run in a SINGLE THREAD (no GIL issues!)
# 4. Use asyncio.sleep(), NOT time.sleep() in async code
# 5. gather() returns results in the same order as inputs
#
# =============================================================================