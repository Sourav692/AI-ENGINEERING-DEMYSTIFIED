"""
=============================================================================
DAEMON THREADS: BACKGROUND WORKERS THAT AUTO-TERMINATE
=============================================================================

What is a Daemon Thread?
------------------------
A DAEMON thread is a "background" thread that:
  - Runs independently of the main program
  - Is AUTOMATICALLY KILLED when the main program exits
  - Does NOT prevent the program from exiting

Think of it like a butler who leaves when the master leaves the house.

Daemon vs Non-Daemon (Regular) Threads:
---------------------------------------
┌─────────────────────┬─────────────────────┬─────────────────────────────┐
│ Aspect              │ Daemon Thread       │ Regular Thread              │
├─────────────────────┼─────────────────────┼─────────────────────────────┤
│ Program exit        │ Terminates thread   │ Waits for thread to finish  │
│ Use case            │ Background tasks    │ Important tasks             │
│ Cleanup             │ May not complete    │ Completes before exit       │
│ Default             │ daemon=True         │ daemon=False (default)      │
└─────────────────────┴─────────────────────┴─────────────────────────────┘

Visual Timeline:
----------------
DAEMON THREAD:
    Main:   ████████████████|EXIT|
    Thread: ████████████████|KILLED| ← Stops abruptly when main exits!
    
NON-DAEMON THREAD (see 08_non_daemon.py):
    Main:   ████████████████|waits...|EXIT|
    Thread: ████████████████████████████████████| ← Main waits for this!

When to Use Daemon Threads:
---------------------------
✅ Monitoring/health checks (don't need to complete)
✅ Logging that can be interrupted
✅ Background polling
✅ Tasks that are OK to terminate abruptly

When NOT to Use:
----------------
❌ File writing (may corrupt data if killed mid-write)
❌ Database transactions (may leave incomplete)
❌ Any task that MUST complete

=============================================================================
"""

import threading  # For creating threads
import time       # For simulating work


def monitor_tea_temp():
    """
    A background monitoring function that runs continuously.
    
    This simulates a temperature monitoring system that checks
    every 2 seconds. As a daemon thread, it will be automatically
    killed when the main program exits.
    
    WARNING: Because this is a daemon thread, it may be killed
    mid-execution! Don't use for critical operations.
    """
    while True:  # Infinite loop - runs forever (or until killed)
        print(f"🌡️  Monitoring tea temperature...")
        time.sleep(2)  # Check every 2 seconds


# =============================================================================
# CREATING A DAEMON THREAD
# =============================================================================
#
# daemon=True tells Python:
#   "This thread is not important. Kill it when the main program exits."
#
# Without daemon=True, the program would run FOREVER because
# the thread has an infinite loop!

print("=" * 50)
print("👻 DAEMON THREAD DEMO")
print("=" * 50)
print("Starting daemon thread (background monitor)...\n")

t = threading.Thread(target=monitor_tea_temp, daemon=True)
t.start()

# =============================================================================
# MAIN PROGRAM COMPLETES IMMEDIATELY
# =============================================================================
#
# The main program doesn't wait for the daemon thread!
# It prints "done" and exits, KILLING the daemon thread.
#
# You might see 0-1 "Monitoring" messages before the thread is killed,
# depending on timing.

print("✅ Main program done")
print("   (Daemon thread will be killed now!)")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ==================================================
# 👻 DAEMON THREAD DEMO
# ==================================================
# Starting daemon thread (background monitor)...
#
# ✅ Main program done
#    (Daemon thread will be killed now!)
#
# Note: The thread may not even print once before being killed!
# The main program exits immediately, killing the daemon.
#
# Compare with 08_non_daemon.py to see the difference!
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. daemon=True creates a background thread that auto-terminates
# 2. Main program does NOT wait for daemon threads to finish
# 3. Daemon threads may be killed abruptly (mid-execution!)
# 4. Perfect for monitoring, logging, background polling
# 5. NOT suitable for critical operations that must complete
#
# =============================================================================