"""
=============================================================================
INTER-PROCESS COMMUNICATION: QUEUE
=============================================================================

The Problem:
------------
Processes have SEPARATE memory spaces. They can't share variables like
threads can. So how do processes communicate?

The Solution: multiprocessing.Queue
------------------------------------
A Queue is a thread/process-safe FIFO (First-In-First-Out) data structure
that allows processes to send messages to each other.

How Queue Works:
----------------
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │    Process 1    │     │      Queue      │     │   Main Process  │
    │                 │     │  ┌───────────┐  │     │                 │
    │  queue.put(msg) │────►│  │ message 1 │  │     │                 │
    │                 │     │  │ message 2 │  │────►│  queue.get()    │
    │                 │     │  │    ...    │  │     │                 │
    └─────────────────┘     │  └───────────┘  │     └─────────────────┘
                            └─────────────────┘
    
    Producer (child)        Shared Queue           Consumer (main)
    puts items in           thread-safe!           gets items out

Key Features:
-------------
✅ Thread-safe and process-safe (no locks needed!)
✅ FIFO ordering (first in, first out)
✅ Blocking get() waits for items
✅ Works across process boundaries

Common Use Cases:
-----------------
- Producer-Consumer pattern
- Collecting results from worker processes
- Task distribution to worker pools
- Logging from multiple processes

=============================================================================
"""

from multiprocessing import Process, Queue  # Process and Queue for IPC


def prepare_chai(queue):
    """
    A worker function that prepares chai and sends result via Queue.
    
    Args:
        queue (Queue): A multiprocessing Queue to send results back
    
    This function demonstrates the PRODUCER side of the Queue pattern:
    - Performs some work (preparing chai)
    - Puts the result into the queue
    - The main process can then retrieve this result
    """
    # Do some work (simulated here)
    result = "☕ Masala chai is ready!"
    
    # =========================================================================
    # SENDING DATA BACK TO MAIN PROCESS
    # =========================================================================
    # queue.put() adds an item to the queue
    # This is how child processes communicate with the main process!
    # 
    # The data is SERIALIZED (pickled) and sent through the queue.
    # This works across process boundaries because Queue uses
    # inter-process communication under the hood.
    
    queue.put(result)
    print(f"📤 Worker: Put '{result}' into queue")


# =============================================================================
# REQUIRED: if __name__ == "__main__" GUARD
# =============================================================================

if __name__ == '__main__':
    
    print("=" * 60)
    print("📬 INTER-PROCESS COMMUNICATION: Queue Demo")
    print("=" * 60)
    print("Child process will send a message to main process...\n")
    
    # =========================================================================
    # CREATE A QUEUE FOR COMMUNICATION
    # =========================================================================
    # This Queue can be shared between processes!
    # It handles all the serialization and IPC internally.
    
    queue = Queue()
    
    # =========================================================================
    # CREATE AND RUN CHILD PROCESS
    # =========================================================================
    # Pass the queue to the child process so it can send data back
    
    p = Process(target=prepare_chai, args=(queue,))
    p.start()  # Start the child process
    p.join()   # Wait for it to complete
    
    # =========================================================================
    # RECEIVE DATA FROM CHILD PROCESS
    # =========================================================================
    # queue.get() retrieves and removes the first item from the queue
    # If the queue is empty, it BLOCKS until an item is available
    
    message = queue.get()
    print(f"📥 Main: Received '{message}' from queue")
    
    print("\n✅ Inter-process communication successful!")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 📬 INTER-PROCESS COMMUNICATION: Queue Demo
# ============================================================
# Child process will send a message to main process...
#
# 📤 Worker: Put '☕ Masala chai is ready!' into queue
# 📥 Main: Received '☕ Masala chai is ready!' from queue
#
# ✅ Inter-process communication successful!
#
# =============================================================================

# =============================================================================
# ADVANCED QUEUE PATTERNS
# =============================================================================
#
# 1. MULTIPLE PRODUCERS:
#     queue = Queue()
#     workers = [Process(target=worker, args=(queue, i)) for i in range(4)]
#     for w in workers: w.start()
#     for w in workers: w.join()
#     
#     # Collect all results
#     while not queue.empty():
#         print(queue.get())
#
# 2. NON-BLOCKING GET:
#     try:
#         item = queue.get_nowait()  # Raises Empty if queue is empty
#     except queue.Empty:
#         print("Queue is empty!")
#
# 3. TIMEOUT GET:
#     try:
#         item = queue.get(timeout=5)  # Wait up to 5 seconds
#     except queue.Empty:
#         print("Timed out waiting for item!")
#
# 4. SENTINEL VALUE (signal workers to stop):
#     queue.put(None)  # Main sends stop signal
#     
#     # In worker:
#     while True:
#         item = queue.get()
#         if item is None:
#             break  # Stop signal received
#         process(item)
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Processes have separate memory - can't share variables directly
# 2. Queue provides safe inter-process communication
# 3. queue.put() sends data, queue.get() receives data
# 4. Data is automatically serialized (pickled) for transfer
# 5. Queue is thread-safe AND process-safe (no locks needed!)
#
# =============================================================================