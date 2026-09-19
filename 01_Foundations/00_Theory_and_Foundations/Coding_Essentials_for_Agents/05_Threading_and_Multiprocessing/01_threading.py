"""
=============================================================================
INTRODUCTION TO THREADING IN PYTHON
=============================================================================

What is Threading?
------------------
Threading allows multiple tasks to run concurrently within a single process.
Think of it like a chai shop where one person takes orders while another 
brews chai - both happen at the same time!

Key Concepts:
-------------
1. Thread: A separate flow of execution within a program
2. Concurrency: Multiple tasks making progress at the same time
3. GIL (Global Interpreter Lock): Python's mechanism that allows only one 
   thread to execute Python bytecode at a time (more on this in later lessons)

When to use Threading:
----------------------
- I/O-bound tasks (file operations, network requests, user input)
- Tasks that spend time waiting (like our time.sleep() examples)
- NOT ideal for CPU-intensive computations (use multiprocessing instead)

Real-world Analogy:
-------------------
Imagine a chai shop:
- Task 1: Taking orders from customers (I/O-bound - waiting for customer)
- Task 2: Brewing chai (I/O-bound - waiting for chai to brew)
Both can happen simultaneously, making the shop more efficient!

=============================================================================
"""

import threading  # Python's built-in module for creating and managing threads
import time       # Used to simulate work with sleep()


def take_orders():
    """
    Simulates taking orders from customers.
    
    This function represents an I/O-bound task where we wait for 
    customer input. Each order takes 2 seconds to process.
    """
    for i in range(1, 4):
        print(f"📝 Taking order for #{i}")
        # time.sleep() simulates waiting time (e.g., customer deciding)
        # During sleep, Python can switch to other threads
        time.sleep(2)


def brew_chai():
    """
    Simulates brewing chai for customers.
    
    This function represents another I/O-bound task where we wait 
    for chai to brew. Each chai takes 3 seconds to prepare.
    """
    for i in range(1, 4):
        print(f"☕ Brewing chai for #{i}")
        # time.sleep() simulates the brewing time
        # While one chai brews, we can take more orders!
        time.sleep(3)


# =============================================================================
# CREATING THREADS
# =============================================================================
# threading.Thread() creates a new thread object
# Parameters:
#   - target: The function to run in this thread
#   - args: Tuple of arguments to pass to the function (optional)
#   - name: A name for the thread for debugging (optional)

order_thread = threading.Thread(target=take_orders)
brew_thread = threading.Thread(target=brew_chai)

# At this point, threads are created but NOT running yet!
# They are in "new" state, waiting to be started.


# =============================================================================
# STARTING THREADS
# =============================================================================
# .start() begins execution of the thread
# The thread will run concurrently with other threads

print("🚀 Starting the chai shop operations...\n")

order_thread.start()  # Starts taking orders in a separate thread
brew_thread.start()   # Starts brewing chai in another separate thread

# IMPORTANT: After .start(), both threads run CONCURRENTLY
# The main program continues to the next line immediately
# It does NOT wait for the threads to finish!


# =============================================================================
# JOINING THREADS (Waiting for Completion)
# =============================================================================
# .join() blocks the main thread until the specified thread completes
# This ensures we don't print "All done" before work is actually done

order_thread.join()  # Wait for all orders to be taken
brew_thread.join()   # Wait for all chai to be brewed

# Only after BOTH threads complete, we reach this line
print("\n✅ All orders taken and chai brewed!")


# =============================================================================
# EXPECTED OUTPUT (order may vary due to concurrent execution):
# =============================================================================
# 🚀 Starting the chai shop operations...
#
# 📝 Taking order for #1
# ☕ Brewing chai for #1
# 📝 Taking order for #2
# ☕ Brewing chai for #2
# 📝 Taking order for #3
# ☕ Brewing chai for #3
#
# ✅ All orders taken and chai brewed!
#
# Note: The interleaving of print statements shows concurrent execution!
# =============================================================================

# =============================================================================
# TIME COMPARISON
# =============================================================================
# Without threading (sequential):
#   - Orders: 3 × 2s = 6 seconds
#   - Brewing: 3 × 3s = 9 seconds
#   - Total: 15 seconds
#
# With threading (concurrent):
#   - Both happen simultaneously
#   - Total: ~9 seconds (limited by the longer task)
#
# That's a 40% time savings! 🎉
# =============================================================================