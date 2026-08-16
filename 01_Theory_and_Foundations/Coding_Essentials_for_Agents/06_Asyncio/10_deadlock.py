"""
=============================================================================
DEADLOCK: WHEN THREADS FREEZE FOREVER
=============================================================================

What is a Deadlock?
-------------------
A DEADLOCK occurs when two or more threads are WAITING FOR EACH OTHER
to release resources, creating a circular dependency where NOBODY can proceed.

It's like two people in a narrow hallway, each waiting for the other to move!

The Deadlock in This Script:
----------------------------
    Task 1 wants: Lock A, then Lock B
    Task 2 wants: Lock B, then Lock A

    What happens:
    ─────────────
    Task 1: Acquires Lock A ✓
    Task 2: Acquires Lock B ✓
    Task 1: Waiting for Lock B... (held by Task 2) 🔒
    Task 2: Waiting for Lock A... (held by Task 1) 🔒
    
    Both threads are now FROZEN FOREVER! 💀

Visual Representation:
----------------------
    ┌─────────────┐                    ┌─────────────┐
    │   Task 1    │ ──── wants ────►   │   Lock B    │
    │  (has A)    │                    │  (held by   │
    └─────────────┘                    │   Task 2)   │
          ▲                            └─────────────┘
          │                                   │
        holds                               holds
          │                                   │
    ┌─────────────┐                    ┌─────────────┐
    │   Lock A    │ ◄──── wants ────   │   Task 2    │
    │  (held by   │                    │  (has B)    │
    │   Task 1)   │                    └─────────────┘
    └─────────────┘
    
                    CIRCULAR WAIT = DEADLOCK!

WARNING:
--------
⚠️  This script will FREEZE and never complete!
⚠️  Use Ctrl+C to stop it!
⚠️  This demonstrates a common threading bug.

=============================================================================
"""

import threading  # For creating threads and locks


# =============================================================================
# CREATE TWO LOCKS
# =============================================================================
# Locks are used to protect critical sections.
# The problem arises when multiple locks are acquired in DIFFERENT ORDERS.

lock_a = threading.Lock()
lock_b = threading.Lock()


def task1():
    """
    Task 1 acquires locks in order: A → B
    
    This creates a potential deadlock when Task 2 acquires in order: B → A
    """
    # Acquire lock A first
    with lock_a:
        print("🔵 Task 1 acquired lock A")
        
        # Small delay makes deadlock more likely to occur
        # (gives Task 2 time to acquire Lock B)
        import time
        time.sleep(0.1)
        
        # Now try to acquire lock B
        # But Task 2 already has it and is waiting for Lock A!
        print("🔵 Task 1 waiting for lock B...")
        with lock_b:
            print("🔵 Task 1 acquired lock B")  # Never reached!


def task2():
    """
    Task 2 acquires locks in order: B → A (OPPOSITE of Task 1!)
    
    This opposite ordering is what causes the deadlock.
    """
    # Acquire lock B first
    with lock_b:
        print("🟢 Task 2 acquired lock B")
        
        # Small delay makes deadlock more likely to occur
        import time
        time.sleep(0.1)
        
        # Now try to acquire lock A
        # But Task 1 already has it and is waiting for Lock B!
        print("🟢 Task 2 waiting for lock A...")
        with lock_a:
            print("🟢 Task 2 acquired lock A")  # Never reached!


# =============================================================================
# CREATE AND START THREADS
# =============================================================================

print("=" * 50)
print("💀 DEADLOCK DEMONSTRATION")
print("=" * 50)
print("Two threads acquiring locks in opposite order...")
print("⚠️  This will FREEZE! Press Ctrl+C to stop!\n")

t1 = threading.Thread(target=task1)
t2 = threading.Thread(target=task2)

t1.start()
t2.start()

# These joins will NEVER complete due to deadlock!
t1.join()
t2.join()

print("✅ Both tasks completed")  # This will NEVER be printed!


# =============================================================================
# EXPECTED OUTPUT (PROGRAM FREEZES!)
# =============================================================================
#
# ==================================================
# 💀 DEADLOCK DEMONSTRATION
# ==================================================
# Two threads acquiring locks in opposite order...
# ⚠️  This will FREEZE! Press Ctrl+C to stop!
#
# 🔵 Task 1 acquired lock A
# 🟢 Task 2 acquired lock B
# 🔵 Task 1 waiting for lock B...
# 🟢 Task 2 waiting for lock A...
#
# (FROZEN - both threads waiting forever!)
# (Press Ctrl+C to terminate)
#
# =============================================================================

# =============================================================================
# THE FOUR CONDITIONS FOR DEADLOCK (Coffman Conditions)
# =============================================================================
#
# A deadlock can occur when ALL FOUR conditions are present:
#
# 1. MUTUAL EXCLUSION: Resources can't be shared (locks are exclusive)
# 2. HOLD AND WAIT: Thread holds one resource while waiting for another
# 3. NO PREEMPTION: Resources can't be forcibly taken from threads
# 4. CIRCULAR WAIT: Thread A waits for B, B waits for A (circular chain)
#
# Breaking ANY ONE of these conditions prevents deadlock!
#
# =============================================================================

# =============================================================================
# HOW TO PREVENT DEADLOCKS
# =============================================================================
#
# 1. CONSISTENT LOCK ORDERING (Most Common Solution)
#    Always acquire locks in the SAME ORDER:
#    
#    def task1():
#        with lock_a:          # Always A first
#            with lock_b:      # Then B
#                ...
#    
#    def task2():
#        with lock_a:          # Always A first (same order!)
#            with lock_b:      # Then B
#                ...
#
# 2. LOCK TIMEOUT
#    Use acquire() with timeout instead of blocking forever:
#    
#    if lock_a.acquire(timeout=1):
#        try:
#            if lock_b.acquire(timeout=1):
#                try:
#                    ...
#                finally:
#                    lock_b.release()
#            else:
#                print("Couldn't get lock B, backing off")
#        finally:
#            lock_a.release()
#
# 3. TRY-LOCK PATTERN
#    Try to acquire, back off if can't:
#    
#    while True:
#        with lock_a:
#            if lock_b.acquire(blocking=False):  # Non-blocking try
#                try:
#                    ...
#                    break
#                finally:
#                    lock_b.release()
#        time.sleep(0.1)  # Back off and retry
#
# 4. USE HIGHER-LEVEL CONSTRUCTS
#    - threading.RLock() - Reentrant lock (same thread can acquire twice)
#    - queue.Queue() - Thread-safe data passing
#    - concurrent.futures - Higher-level concurrency
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Deadlock = threads waiting for each other forever (circular wait)
# 2. Caused by acquiring multiple locks in DIFFERENT ORDERS
# 3. Program FREEZES - no error message, just hangs!
# 4. PREVENTION: Always acquire locks in the SAME ORDER
# 5. DETECTION: Use timeouts to avoid infinite waiting
#
# =============================================================================