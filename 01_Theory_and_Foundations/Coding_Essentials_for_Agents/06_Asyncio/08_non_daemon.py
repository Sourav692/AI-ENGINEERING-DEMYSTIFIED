"""
=============================================================================
NON-DAEMON (REGULAR) THREADS: THREADS THAT MUST COMPLETE
=============================================================================

What is a Non-Daemon Thread?
----------------------------
A NON-DAEMON (regular) thread is the DEFAULT behavior:
  - The main program WAITS for it to finish before exiting
  - It is considered "important" and must complete its work
  - The program cannot exit until ALL non-daemon threads finish

Compare with 07_daemon.py to see the difference!

The Problem with This Script:
-----------------------------
This script will RUN FOREVER because:
  1. The thread has an infinite loop (while True)
  2. It's NOT a daemon thread (default: daemon=False)
  3. The main program WAITS for it to finish... which never happens!

Visual Timeline:
----------------
NON-DAEMON THREAD (this script):
    Main:   ████|"done"|waits forever...
    Thread: ████████████████████████████████████...forever...
    
    Main program prints "done" but can't exit!
    You'll have to press Ctrl+C to stop it.

DAEMON THREAD (07_daemon.py):
    Main:   ████████████████|EXIT|
    Thread: ████████████████|KILLED| ← Clean exit!

WARNING:
--------
⚠️  This script will run INDEFINITELY!
⚠️  Use Ctrl+C to stop it!
⚠️  This demonstrates what happens when you forget daemon=True
    for background tasks with infinite loops.

=============================================================================
"""

import threading  # For creating threads
import time       # For simulating work


def monitor_tea_temp():
    """
    A monitoring function with an infinite loop.
    
    As a NON-DAEMON thread (default), the main program will
    wait for this function to complete... which NEVER happens!
    
    This demonstrates why daemon=True is important for
    background tasks that run indefinitely.
    """
    while True:  # Infinite loop - NEVER stops!
        print(f"🌡️  Monitoring tea temperature...")
        time.sleep(2)


# =============================================================================
# CREATING A NON-DAEMON THREAD (DEFAULT)
# =============================================================================
#
# Notice: We're NOT setting daemon=True
# This means the thread is a "regular" thread.
# The main program will WAIT for it to finish before exiting.
#
# But since the thread has an infinite loop, it NEVER finishes!
# Result: Program runs forever!

print("=" * 50)
print("🔄 NON-DAEMON THREAD DEMO")
print("=" * 50)
print("Starting non-daemon thread (will run forever!)...")
print("⚠️  Press Ctrl+C to stop!\n")

t = threading.Thread(target=monitor_tea_temp)  # daemon=False by default!
t.start()

# =============================================================================
# MAIN PROGRAM "COMPLETES" BUT CAN'T EXIT
# =============================================================================
#
# This print statement executes immediately, but...
# Python won't exit because the non-daemon thread is still running!
#
# The program will keep printing "Monitoring..." every 2 seconds forever.

print("✅ Main program done")
print("   (But waiting for thread to finish... which is never!)")
print("   Press Ctrl+C to exit.\n")


# =============================================================================
# EXPECTED OUTPUT (runs forever until Ctrl+C!)
# =============================================================================
#
# ==================================================
# 🔄 NON-DAEMON THREAD DEMO
# ==================================================
# Starting non-daemon thread (will run forever!)...
# ⚠️  Press Ctrl+C to stop!
#
# ✅ Main program done
#    (But waiting for thread to finish... which is never!)
#    Press Ctrl+C to exit.
#
# 🌡️  Monitoring tea temperature...
# 🌡️  Monitoring tea temperature...
# 🌡️  Monitoring tea temperature...
# ... (continues forever until Ctrl+C)
#
# =============================================================================

# =============================================================================
# THE FIX
# =============================================================================
#
# Option 1: Make it a daemon thread
#     t = threading.Thread(target=monitor_tea_temp, daemon=True)
#
# Option 2: Add a stop condition to the loop
#     stop_flag = threading.Event()
#     
#     def monitor_tea_temp():
#         while not stop_flag.is_set():
#             print("Monitoring...")
#             time.sleep(2)
#     
#     # Later: stop_flag.set() to stop the thread
#
# Option 3: Don't use infinite loops for non-daemon threads!
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Non-daemon threads (default) prevent program exit
# 2. Main program waits for ALL non-daemon threads to complete
# 3. Infinite loops + non-daemon = program runs forever!
# 4. Use daemon=True for background tasks with infinite loops
# 5. Or use stop conditions (Event, flag) to control thread termination
#
# =============================================================================