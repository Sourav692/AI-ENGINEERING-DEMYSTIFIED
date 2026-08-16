"""
=============================================================================
REAL-WORLD ASYNC: HTTP REQUESTS WITH AIOHTTP
=============================================================================

Why aiohttp?
------------
The popular `requests` library is SYNCHRONOUS (blocking). It doesn't work
well with asyncio because it blocks the entire event loop during requests.

`aiohttp` is the ASYNC alternative - designed specifically for asyncio!

requests vs aiohttp:
--------------------
┌─────────────────────┬────────────────────────────────────────────────────┐
│ requests (sync)     │ aiohttp (async)                                    │
├─────────────────────┼────────────────────────────────────────────────────┤
│ resp = requests.get │ async with session.get(url) as resp                │
│ Blocks event loop   │ Yields control during network wait                 │
│ One request at time │ Many requests concurrently                         │
│ Simple, familiar    │ Slightly more complex, but much faster!            │
└─────────────────────┴────────────────────────────────────────────────────┘

This Script Demonstrates:
-------------------------
Making 3 HTTP requests that each take 2 seconds.
  - Sequential (requests): 2 + 2 + 2 = 6 seconds
  - Concurrent (aiohttp): max(2, 2, 2) = ~2 seconds!

That's 3x faster for the same work!

Installation:
-------------
    pip install aiohttp

=============================================================================
"""

import asyncio  # Python's async library
import aiohttp  # Async HTTP client library (pip install aiohttp)


async def fetch_url(session, url):
    """
    Fetches a URL asynchronously using the provided session.
    
    Args:
        session (aiohttp.ClientSession): Reusable HTTP session
        url (str): The URL to fetch
    
    Key Concepts:
    -------------
    1. We pass the SESSION, not create a new one for each request
       - Sessions manage connection pooling (reuse connections)
       - More efficient than creating new connections each time
    
    2. We use `async with` for the response
       - This is an async context manager
       - Ensures proper cleanup of the response
    """
    # =========================================================================
    # ASYNC CONTEXT MANAGER: async with
    # =========================================================================
    # 
    # `async with session.get(url) as response:`
    #
    # This is similar to regular `with`, but for async operations.
    # It properly handles setup and cleanup in an async context.
    # The response object is available inside the block.
    
    async with session.get(url) as response:
        print(f"✅ Fetched {url} with status {response.status}")
        # You can also get the content:
        # data = await response.text()     # For text content
        # data = await response.json()     # For JSON content
        # data = await response.read()     # For binary content


async def main():
    """
    Main coroutine that fetches multiple URLs concurrently.
    """
    print("=" * 60)
    print("🌐 ASYNC HTTP CLIENT: Concurrent Requests with aiohttp")
    print("=" * 60)
    
    # =========================================================================
    # TEST URLs
    # =========================================================================
    # httpbin.org/delay/2 waits 2 seconds before responding
    # We're making 3 requests, each with a 2-second delay
    
    urls = ["https://httpbin.org/delay/2"] * 3  # 3 identical URLs
    
    print(f"Fetching {len(urls)} URLs (each has 2-second delay)...\n")
    
    import time
    start = time.time()
    
    # =========================================================================
    # AIOHTTP CLIENT SESSION
    # =========================================================================
    #
    # aiohttp.ClientSession() is like a "browser session":
    #   - Manages cookies across requests
    #   - Reuses TCP connections (connection pooling)
    #   - Should be created ONCE and reused for multiple requests
    #
    # Always use `async with` to ensure proper cleanup!
    
    async with aiohttp.ClientSession() as session:
        
        # =====================================================================
        # CREATE TASKS FROM COROUTINES
        # =====================================================================
        # 
        # List comprehension creates a list of coroutines
        # Each coroutine will fetch one URL using the shared session
        
        tasks = [fetch_url(session, url) for url in urls]
        # tasks = [coroutine1, coroutine2, coroutine3]
        
        # =====================================================================
        # RUN ALL TASKS CONCURRENTLY WITH GATHER
        # =====================================================================
        #
        # The * operator UNPACKS the list:
        #   asyncio.gather(*tasks)
        # is equivalent to:
        #   asyncio.gather(tasks[0], tasks[1], tasks[2])
        #
        # This starts ALL requests at the same time!
        
        await asyncio.gather(*tasks)
    
    end = time.time()
    print(f"\n🎉 All requests completed in {end - start:.2f} seconds!")
    print("   (3 requests × 2 seconds each, but only ~2 seconds total!)")


# Run the main coroutine
asyncio.run(main())


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🌐 ASYNC HTTP CLIENT: Concurrent Requests with aiohttp
# ============================================================
# Fetching 3 URLs (each has 2-second delay)...
#
# ✅ Fetched https://httpbin.org/delay/2 with status 200
# ✅ Fetched https://httpbin.org/delay/2 with status 200
# ✅ Fetched https://httpbin.org/delay/2 with status 200
#
# 🎉 All requests completed in 2.15 seconds!
#    (3 requests × 2 seconds each, but only ~2 seconds total!)
#
# =============================================================================

# =============================================================================
# COMMON AIOHTTP PATTERNS
# =============================================================================
#
# 1. GET request with parameters:
#     async with session.get(url, params={"key": "value"}) as resp:
#         data = await resp.json()
#
# 2. POST request with JSON body:
#     async with session.post(url, json={"name": "chai"}) as resp:
#         result = await resp.json()
#
# 3. Handling errors:
#     try:
#         async with session.get(url) as resp:
#             resp.raise_for_status()  # Raises if status >= 400
#             data = await resp.text()
#     except aiohttp.ClientError as e:
#         print(f"Request failed: {e}")
#
# 4. Setting timeout:
#     timeout = aiohttp.ClientTimeout(total=10)
#     async with aiohttp.ClientSession(timeout=timeout) as session:
#         ...
#
# =============================================================================

# =============================================================================
# KEY TAKEAWAYS
# =============================================================================
#
# 1. Use aiohttp for async HTTP requests (not requests library)
# 2. Create ONE ClientSession and reuse it for all requests
# 3. Use `async with` for both session and response
# 4. asyncio.gather(*tasks) runs all requests concurrently
# 5. Total time = slowest request, not sum of all requests
#
# =============================================================================