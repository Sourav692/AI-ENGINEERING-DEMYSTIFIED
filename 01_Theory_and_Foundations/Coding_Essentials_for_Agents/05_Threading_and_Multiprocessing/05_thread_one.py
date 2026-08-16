"""
=============================================================================
PRACTICAL THREADING EXAMPLE: MAKING BREAKFAST CONCURRENTLY
=============================================================================

Real-World Scenario:
--------------------
Imagine making breakfast. You need to:
  1. Boil milk (takes 2 seconds)
  2. Toast a bun (takes 3 seconds)

Sequential Approach (one after another):
  Boil milk → Toast bun = 2 + 3 = 5 seconds total

Concurrent Approach (both at same time):
  Boil milk ─┬─ (both happen simultaneously)
  Toast bun ─┘  = max(2, 3) = 3 seconds total

That's a 40% time savings! 🎉

Why Threading Works Here:
-------------------------
Both tasks are I/O-BOUND (waiting for something external):
  - Boiling milk = waiting for heat
  - Toasting bun = waiting for toaster

During the wait (time.sleep), Python releases the GIL, allowing other
threads to run. This is why threading is PERFECT for I/O-bound tasks!

Visual Timeline:
----------------
SEQUENTIAL:
  |←── Boil Milk (2s) ──→|←──── Toast Bun (3s) ────→|
  |─────────────────────────────────────────────────| = 5 seconds

CONCURRENT (Threading):
  |←── Boil Milk (2s) ──→|
  |←────── Toast Bun (3s) ───────→|
  |──────────────────────────────| = 3 seconds (limited by longest task)

=============================================================================
"""

import threading  # Python's built-in threading module
import time       # For simulating work and measuring execution time


def boil_milk():
    """
    Simulates boiling milk - an I/O-bound task.
    
    In real life, you're waiting for the stove to heat the milk.
    In code, time.sleep() simulates this waiting period.
    During sleep, the GIL is released, allowing other threads to run!
    """
    print(f"🥛 Boiling milk...")
    time.sleep(2)  # Simulates 2 seconds of waiting for milk to boil
    print(f"✅ Milk boiled!")


def toast_bun():
    """
    Simulates toasting a bun - an I/O-bound task.
    
    In real life, you're waiting for the toaster to finish.
    While the toaster works, you can do other things (like boil milk)!
    """
    print(f"🍞 Toasting bun...")
    time.sleep(3)  # Simulates 3 seconds of waiting for bun to toast
    print(f"✅ Bun toasted!")


# =============================================================================
# TIMING THE CONCURRENT EXECUTION
# =============================================================================
# We measure total time to demonstrate the benefit of threading

print("=" * 50)
print("🍳 BREAKFAST MAKER: Threading Demo")
print("=" * 50)
print("Making breakfast with concurrent tasks...\n")

start = time.time()  # Record start time

# =============================================================================
# CREATE THREAD OBJECTS
# =============================================================================
# Each Thread object represents a separate flow of execution
# target: The function to run in this thread

t1 = threading.Thread(target=boil_milk)  # Thread for boiling milk
t2 = threading.Thread(target=toast_bun)  # Thread for toasting bun

# At this point, threads are created but NOT running yet!


# =============================================================================
# START THREADS (Begin Concurrent Execution)
# =============================================================================
# .start() begins execution of each thread
# After starting, both tasks run CONCURRENTLY!

t1.start()  # Start boiling milk in the background
t2.start()  # Start toasting bun in the background

# IMPORTANT: The main thread continues immediately!
# It does NOT wait for t1 and t2 to finish.
# All three "threads" are now running:
#   - Main thread (this script)
#   - t1 (boiling milk)
#   - t2 (toasting bun)


# =============================================================================
# JOIN THREADS (Wait for Completion)
# =============================================================================
# .join() makes the main thread WAIT until the specified thread finishes
# Without join(), we might print "Breakfast is ready" before tasks complete!

t1.join()  # Wait for milk to finish boiling
t2.join()  # Wait for bun to finish toasting

# Only after BOTH threads complete, we continue to the next line

end = time.time()  # Record end time

print(f"\n🎉 Breakfast is ready in {end - start:.2f} seconds!")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
# 
# ==================================================
# 🍳 BREAKFAST MAKER: Threading Demo
# ==================================================
# Making breakfast with concurrent tasks...
# 
# 🥛 Boiling milk...
# 🍞 Toasting bun...
# ✅ Milk boiled!        ← Finishes after 2 seconds
# ✅ Bun toasted!        ← Finishes after 3 seconds
# 
# 🎉 Breakfast is ready in 3.00 seconds!
#
# Note: Both tasks started almost simultaneously!
# Total time = max(2s, 3s) = 3 seconds, NOT 2s + 3s = 5 seconds
#
# =============================================================================

# =============================================================================
# TIME COMPARISON SUMMARY
# =============================================================================
#
# ┌─────────────────────┬────────────────┬───────────────────────────────────┐
# │ Approach            │ Time           │ Calculation                       │
# ├─────────────────────┼────────────────┼───────────────────────────────────┤
# │ Sequential          │ ~5 seconds     │ 2s (milk) + 3s (bun) = 5s         │
# │ Concurrent          │ ~3 seconds     │ max(2s, 3s) = 3s                  │
# └─────────────────────┴────────────────┴───────────────────────────────────┘
#
# Speedup: (5 - 3) / 5 = 40% faster! ⚡
#
# =============================================================================

# =============================================================================
# KEY CONCEPTS DEMONSTRATED
# =============================================================================
#
# 1. I/O-BOUND TASKS: Both tasks involve "waiting" (simulated by sleep)
#    - While waiting, CPU is idle → perfect for threading!
#    
# 2. CONCURRENT EXECUTION: Both tasks run at the same time
#    - Total time = time of the LONGEST task
#    
# 3. GIL RELEASE: During time.sleep(), Python releases the GIL
#    - Other threads can run during this time
#    
# 4. REAL-WORLD PARALLEL: Just like in a real kitchen:
#    - You don't wait for milk to boil before putting bread in the toaster!
#    - You do both at the same time to save time
#
# =============================================================================