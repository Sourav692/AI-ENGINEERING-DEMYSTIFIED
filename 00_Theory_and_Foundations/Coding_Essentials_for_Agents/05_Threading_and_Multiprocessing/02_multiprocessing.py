"""
=============================================================================
INTRODUCTION TO MULTIPROCESSING IN PYTHON
=============================================================================

What is Multiprocessing?
------------------------
Multiprocessing allows you to run multiple processes in PARALLEL, each with
its own Python interpreter and memory space. Unlike threading, multiprocessing
can truly utilize multiple CPU cores simultaneously!

Threading vs Multiprocessing:
-----------------------------
┌─────────────────────┬─────────────────────┬─────────────────────────────────┐
│ Aspect              │ Threading           │ Multiprocessing                 │
├─────────────────────┼─────────────────────┼─────────────────────────────────┤
│ Memory              │ Shared memory       │ Separate memory per process     │
│ GIL Impact          │ Affected by GIL     │ Bypasses GIL completely         │
│ CPU Utilization     │ Single core         │ Multiple cores                  │
│ Best For            │ I/O-bound tasks     │ CPU-bound tasks                 │
│ Overhead            │ Low                 │ Higher (process creation)       │
│ Communication       │ Easy (shared vars)  │ Requires IPC (Queue, Pipe)      │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘

Key Concepts:
-------------
1. Process: An independent instance of Python interpreter with its own memory
2. Parallelism: True simultaneous execution on multiple CPU cores
3. GIL Bypass: Each process has its own GIL, enabling true parallel execution

When to use Multiprocessing:
----------------------------
✅ CPU-intensive computations (number crunching, image processing)
✅ Tasks that need true parallelism
✅ When you need to utilize multiple CPU cores
❌ NOT ideal for simple I/O-bound tasks (threading is more efficient)
❌ When you need frequent data sharing between tasks

Real-world Analogy:
-------------------
Imagine 3 separate chai stalls, each with their own:
- Stove (CPU core)
- Ingredients (memory)
- Chai maker (process)
All can brew chai TRULY at the same time, no waiting for each other!

=============================================================================
"""

from multiprocessing import Process  # Import Process class for creating processes
import time                          # Used to simulate work with sleep()


def brew_chai(name):
    """
    Simulates a chai maker brewing chai.
    
    This function runs in a SEPARATE PROCESS with its own:
    - Memory space (variables are NOT shared with main process)
    - Python interpreter instance
    - Global Interpreter Lock (GIL)
    
    Args:
        name (str): Identifier for the chai maker
    """
    print(f"☕ Start of {name} chai brewing")
    # time.sleep() simulates the brewing time
    # Unlike threading, this process runs on a separate CPU core!
    time.sleep(3)
    print(f"✅ End of {name} chai brewing")


# =============================================================================
# CRITICAL: THE if __name__ == "__main__" GUARD
# =============================================================================
# This guard is REQUIRED for multiprocessing on Windows and recommended on all
# platforms. Here's why:
#
# When a new process is spawned, Python imports the main module to set up the
# process. Without this guard, it would try to spawn new processes infinitely!
#
# What happens without it:
#   1. Main script runs → Creates Process
#   2. New Process imports main script → Tries to create another Process
#   3. That Process imports main script → Creates another Process
#   4. ... infinite loop and crash!
#
# The guard ensures process-spawning code only runs in the MAIN process.
# =============================================================================

if __name__ == "__main__":
    
    # =========================================================================
    # CREATING MULTIPLE PROCESSES
    # =========================================================================
    # Using list comprehension to create 3 Process objects
    # 
    # Process() Parameters:
    #   - target: The function to run in the new process
    #   - args: A TUPLE of arguments to pass to the function
    #           Note: (value,) - the comma is required for single-item tuple!
    #   - name: Optional name for the process (for debugging)
    #   - daemon: If True, process terminates when main program exits
    
    chai_makers = [
        Process(target=brew_chai, args=(f"Chai Maker #{i+1}",))
        for i in range(3)
    ]
    # This creates 3 Process objects, but they're NOT running yet!
    # They are in "created" state, waiting to be started.
    
    print("🚀 Starting all chai makers in parallel...\n")
    
    # =========================================================================
    # STARTING ALL PROCESSES
    # =========================================================================
    # .start() spawns a new OS-level process
    # Each process gets its own Python interpreter and memory space
    # All processes run TRULY in parallel on different CPU cores!
    
    for p in chai_makers:
        p.start()
    
    # IMPORTANT: After starting, all 3 processes run SIMULTANEOUSLY
    # The main process continues immediately without waiting
    
    
    # =========================================================================
    # JOINING PROCESSES (Waiting for Completion)
    # =========================================================================
    # .join() blocks the main process until the specified process completes
    # This ensures we don't print "All chai served" before work is done
    #
    # Optional parameter: join(timeout=seconds)
    # - If timeout is specified, join() waits at most that many seconds
    # - Check p.is_alive() to see if process is still running after timeout
    
    for p in chai_makers:
        p.join()
    
    # Only after ALL processes complete, we reach this line
    print("\n🎉 All chai served!")


# =============================================================================
# EXPECTED OUTPUT (order may vary due to parallel execution):
# =============================================================================
# 🚀 Starting all chai makers in parallel...
#
# ☕ Start of Chai Maker #1 chai brewing
# ☕ Start of Chai Maker #2 chai brewing
# ☕ Start of Chai Maker #3 chai brewing
# ✅ End of Chai Maker #1 chai brewing
# ✅ End of Chai Maker #2 chai brewing
# ✅ End of Chai Maker #3 chai brewing
#
# 🎉 All chai served!
#
# Note: All 3 "Start" messages appear almost instantly (parallel execution)
# All 3 "End" messages appear together after ~3 seconds (not 9 seconds!)
# =============================================================================

# =============================================================================
# TIME COMPARISON
# =============================================================================
# Sequential execution:
#   - 3 chai makers × 3 seconds each = 9 seconds total
#
# Parallel execution (multiprocessing):
#   - All 3 run simultaneously = ~3 seconds total
#
# That's 3x faster! True parallelism! 🚀
# =============================================================================

# =============================================================================
# COMMON PITFALLS TO AVOID
# =============================================================================
# 1. Forgetting if __name__ == "__main__" guard → Infinite process spawning
# 2. Trying to share variables directly → Use Queue, Pipe, or Manager instead
# 3. Creating too many processes → Use Pool for better resource management
# 4. Using multiprocessing for simple I/O tasks → Threading is more efficient
# =============================================================================