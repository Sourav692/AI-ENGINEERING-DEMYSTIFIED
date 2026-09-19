"""
=============================================================================
PASSING ARGUMENTS TO THREADS
=============================================================================

New Concept: Thread Arguments
-----------------------------
In previous examples, our thread target functions had no parameters.
But what if we want to pass data to each thread?

The threading.Thread() constructor accepts two key parameters for this:
  - args: A TUPLE of positional arguments
  - kwargs: A DICTIONARY of keyword arguments

This Script Demonstrates:
-------------------------
  - Using `args` to pass different values to the same function
  - Creating reusable, parameterized thread functions
  - Running the same function with different configurations

Real-World Analogy:
-------------------
A chai shop with one recipe (prepare_chai function) but different:
  - Types of chai (Masala, Ginger)
  - Brewing times (2 seconds, 3 seconds)

Instead of writing separate functions for each chai type, we write ONE
flexible function that accepts parameters!

=============================================================================
"""

import threading  # Python's built-in threading module
import time       # For simulating brewing time


def prepare_chai(type_, wait_time):
    """
    Prepares a specific type of chai with a given brewing time.
    
    This is a PARAMETERIZED function that can handle different chai types
    and brewing times based on the arguments passed.
    
    Args:
        type_ (str): The type of chai (e.g., "Masala", "Ginger")
                     Note: We use type_ (with underscore) because 'type' 
                     is a built-in Python function - avoid shadowing it!
        wait_time (int): How long to brew in seconds
    
    Why parameterize?
    -----------------
    Instead of writing:
        def prepare_masala_chai(): ...
        def prepare_ginger_chai(): ...
        def prepare_cardamom_chai(): ...
    
    We write ONE flexible function that handles ALL types!
    """
    print(f"☕ {type_} chai: brewing...")
    time.sleep(wait_time)  # Simulate brewing time
    print(f"✅ {type_} chai: Ready!")


# =============================================================================
# CREATING THREADS WITH ARGUMENTS
# =============================================================================
# 
# threading.Thread() Parameters:
#   - target: The function to run in the thread
#   - args: A TUPLE of positional arguments to pass to the function
#   - kwargs: A DICT of keyword arguments (not used here, but available)
#   - name: Optional name for the thread
#
# IMPORTANT: args must be a TUPLE!
#   ✅ args=("Masala", 2)      - Correct: tuple with 2 elements
#   ❌ args="Masala", 2        - Wrong: not a tuple
#   ✅ args=("Masala",)        - Correct: single-element tuple (note the comma!)
#   ❌ args=("Masala")         - Wrong: just a string in parentheses

print("=" * 50)
print("☕ CHAI SHOP: Parameterized Threading Demo")
print("=" * 50)
print("Brewing two types of chai concurrently...\n")

# Thread 1: Prepare Masala chai (takes 2 seconds)
t1 = threading.Thread(target=prepare_chai, args=("Masala", 2))

# Thread 2: Prepare Ginger chai (takes 3 seconds)  
t2 = threading.Thread(target=prepare_chai, args=("Ginger", 3))

# =============================================================================
# ALTERNATIVE: USING kwargs FOR KEYWORD ARGUMENTS
# =============================================================================
# You can also use kwargs (keyword arguments) instead of args:
#
# t1 = threading.Thread(
#     target=prepare_chai, 
#     kwargs={"type_": "Masala", "wait_time": 2}
# )
#
# Or combine both:
# t1 = threading.Thread(
#     target=prepare_chai, 
#     args=("Masala",),           # First positional arg
#     kwargs={"wait_time": 2}     # Second as keyword arg
# )


# =============================================================================
# START AND JOIN THREADS
# =============================================================================

t1.start()  # Start brewing Masala chai
t2.start()  # Start brewing Ginger chai (concurrently!)

t1.join()   # Wait for Masala chai
t2.join()   # Wait for Ginger chai

print("\n🎉 All chai varieties are ready to serve!")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ==================================================
# ☕ CHAI SHOP: Parameterized Threading Demo
# ==================================================
# Brewing two types of chai concurrently...
#
# ☕ Masala chai: brewing...
# ☕ Ginger chai: brewing...
# ✅ Masala chai: Ready!     ← After 2 seconds
# ✅ Ginger chai: Ready!     ← After 3 seconds
#
# 🎉 All chai varieties are ready to serve!
#
# Note: Both start immediately, Masala finishes first (shorter brew time)
#
# =============================================================================

# =============================================================================
# KEY CONCEPTS DEMONSTRATED
# =============================================================================
#
# 1. ARGS PARAMETER: Pass positional arguments as a tuple
#    threading.Thread(target=func, args=(arg1, arg2, arg3))
#
# 2. KWARGS PARAMETER: Pass keyword arguments as a dictionary
#    threading.Thread(target=func, kwargs={"key1": val1, "key2": val2})
#
# 3. PARAMETERIZED FUNCTIONS: One function, many uses
#    - Same prepare_chai() function for Masala, Ginger, or any other type
#    - More maintainable than separate functions for each variant
#
# 4. TUPLE GOTCHA: Single-element tuples need a trailing comma!
#    - args=("value",)  ✅ Tuple with one element
#    - args=("value")   ❌ Just a string in parentheses
#
# =============================================================================

# =============================================================================
# BONUS: SCALING UP WITH LOOPS
# =============================================================================
# With parameterized functions, you can easily create many threads:
#
# chai_types = [("Masala", 2), ("Ginger", 3), ("Cardamom", 4), ("Plain", 1)]
# threads = []
#
# for chai_type, brew_time in chai_types:
#     t = threading.Thread(target=prepare_chai, args=(chai_type, brew_time))
#     threads.append(t)
#     t.start()
#
# for t in threads:
#     t.join()
#
# This pattern is much cleaner than creating separate functions for each chai!
# =============================================================================