# ============================================================================
# Utility Functions for Educational Examples
# ============================================================================
# This module provides utility functions used across the tutorial files.
# These utilities enhance the educational experience by providing better
# output formatting and performance measurement.
# ============================================================================

from rich.console import Console
import time
import asyncio
import functools
import inspect

# ============================================================================
# Rich Console: Enhanced Print Output
# ============================================================================
# Replace the standard print() with Rich's console.print() for:
# - Better formatting (colors, styles, tables)
# - Improved readability in terminal output
# - More professional-looking output for demonstrations

console = Console()
print = console.print  # Replace built-in print with Rich's enhanced print


# ============================================================================
# Timing Decorator: Measure Execution Time
# ============================================================================

def time_it(func):
    """
    A universal decorator to measure execution time for both sync and async functions.
    
    This decorator works with both synchronous and asynchronous functions,
    automatically detecting the function type and using the appropriate timing logic.
    
    Usage:
        @time_it
        def my_function():
            # Your code here
            pass
        
        @time_it
        async def my_async_function():
            # Your async code here
            pass
    
    The decorator will automatically:
    - Measure execution time
    - Print the elapsed time
    - Return the function's result unchanged
    
    Note: For async functions, the decorator handles awaiting automatically.
    
    Returns:
        Decorated function that measures and reports execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if the function is a coroutine function (async def)
        if inspect.iscoroutinefunction(func):
            # Define and return an async wrapper to handle the coroutine
            async def async_wrapper():
                start_time = time.perf_counter()  # High-resolution timer for accuracy
                result = await func(*args, **kwargs)  # Await the coroutine
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                print(f"Async function '{func.__name__}' took {elapsed_time:.4f} seconds.")
                return result
            return async_wrapper()
        else:
            # Use the original synchronous logic
            start_time = time.perf_counter()  # High-resolution timer for accuracy
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(f"Sync function '{func.__name__}' took {elapsed_time:.4f} seconds.")
            return result
    return wrapper
