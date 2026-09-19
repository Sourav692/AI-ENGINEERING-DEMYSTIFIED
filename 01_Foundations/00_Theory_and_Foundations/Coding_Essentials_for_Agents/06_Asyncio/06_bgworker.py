"""
=============================================================================
COMBINING ASYNCIO WITH BACKGROUND THREADS
=============================================================================

Real-World Scenario:
--------------------
Sometimes you need BOTH:
  1. Async operations (HTTP requests, database queries)
  2. Background tasks that run continuously (logging, monitoring, heartbeats)

This script shows how to run a DAEMON THREAD alongside async code!

Architecture:
-------------
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Main Thread                                                        │
    │  ┌───────────────────────────────────────────────────────────────┐  │
    │  │  Event Loop (asyncio)                                         │  │
    │  │  ┌─────────────────────────────────────────────────────────┐  │  │
    │  │  │  async def fetch_orders()                               │  │  │
    │  │  │  await asyncio.sleep(3)                                 │  │  │
    │  │  │  print("order fetched")                                 │  │  │
    │  │  └─────────────────────────────────────────────────────────┘  │  │
    │  └───────────────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────────────┘
                              ║ runs alongside
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Daemon Thread (background_worker)                                  │
    │  ┌───────────────────────────────────────────────────────────────┐  │
    │  │  while True:                                                  │  │
    │  │      time.sleep(1)                                            │  │
    │  │      print("Logging system health")                           │  │
    │  └───────────────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────────────┘

Why Daemon Thread?
------------------
A daemon thread automatically terminates when the main program exits.
Perfect for background tasks that should stop when the app stops!

=============================================================================
"""

import asyncio    # For async operations
import threading  # For background thread
import time       # For sleep in background worker


def background_worker():
    """
    A background worker that runs continuously in a separate thread.
    
    This simulates a monitoring/logging system that:
    - Runs in an infinite loop
    - Performs periodic tasks (every 1 second)
    - Continues running while async code executes
    
    Because it's a DAEMON thread, it will automatically stop
    when the main program (asyncio.run) completes!
    """
    while True:
        time.sleep(1)  # Wait 1 second between health checks
        print(f"📊 Logging the system health... 🕰️")


async def fetch_orders():
    """
    An async coroutine that simulates fetching orders.
    
    While this coroutine is waiting (await asyncio.sleep),
    the background worker thread continues running and logging!
    """
    print("🔄 Fetching orders from server...")
    await asyncio.sleep(3)  # Simulate network delay
    print("🎁 Order fetched successfully!")


# =============================================================================
# START BACKGROUND THREAD BEFORE ASYNC CODE
# =============================================================================
#
# Key points:
# 1. We start the thread BEFORE asyncio.run()
# 2. daemon=True means thread dies when main program exits
# 3. No need to .join() - it stops automatically

print("=" * 60)
print("🔀 HYBRID PATTERN: Daemon Thread + Asyncio")
print("=" * 60)
print("Starting background worker (daemon thread)...")
print("Then running async operations...\n")

# Start the background worker as a daemon thread
# daemon=True → Thread stops when main program exits
threading.Thread(target=background_worker, daemon=True).start()

# Run the async main coroutine
# The background thread runs ALONGSIDE this!
asyncio.run(fetch_orders())

print("\n✅ Main program complete (daemon thread auto-terminated)")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🔀 HYBRID PATTERN: Daemon Thread + Asyncio
# ============================================================
# Starting background worker (daemon thread)...
# Then running async operations...
#
# 🔄 Fetching orders from server...
# 📊 Logging the system health... 🕰️     ← After 1 second
# 📊 Logging the system health... 🕰️     ← After 2 seconds
# 📊 Logging the system health... 🕰️     ← After 3 seconds
# 🎁 Order fetched successfully!
#
# ✅ Main program complete (daemon thread auto-terminated)
#
# Note: The health logs appear WHILE waiting for orders!
#
# =============================================================================

# =============================================================================
# USE CASES FOR THIS PATTERN
# =============================================================================
#
# 1. HEALTH MONITORING: Periodic health checks while processing requests
# 2. METRICS COLLECTION: Gather stats in background while app runs
# 3. HEARTBEATS: Send keep-alive signals to external services
# 4. LOG ROTATION: Periodically rotate/compress logs
# 5. CACHE REFRESH: Update caches without blocking main operations
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Daemon threads run alongside asyncio event loops
# 2. daemon=True makes threads stop automatically on program exit
# 3. Perfect for continuous background tasks (monitoring, logging)
# 4. Background thread uses time.sleep() (blocking is OK in its own thread)
# 5. Main async code uses asyncio.sleep() (non-blocking)
#
# =============================================================================