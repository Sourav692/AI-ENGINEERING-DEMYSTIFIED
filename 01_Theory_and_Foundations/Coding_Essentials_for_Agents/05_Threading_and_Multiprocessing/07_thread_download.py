"""
=============================================================================
REAL-WORLD THREADING: CONCURRENT FILE DOWNLOADS
=============================================================================

This is Threading's KILLER USE CASE!
------------------------------------
Downloading files from the internet is the PERFECT example of I/O-bound work:
  - Your CPU does almost nothing
  - Most time is spent WAITING for network responses
  - GIL is released during network I/O
  - Threading provides MASSIVE speedup!

Sequential vs Concurrent Downloads:
-----------------------------------
SEQUENTIAL (one at a time):
  |←── Download 1 ──→|←── Download 2 ──→|←── Download 3 ──→|
  |────────────────────────────────────────────────────────| = ~3 seconds

CONCURRENT (all at once with threading):
  |←── Download 1 ──→|
  |←── Download 2 ──→|
  |←── Download 3 ──→|
  |──────────────────| = ~1 second (limited by slowest download)

Pattern Used: Dynamic Thread Creation
-------------------------------------
This script demonstrates a common pattern for handling multiple similar tasks:
  1. Store URLs (or tasks) in a list
  2. Loop through the list to create and start threads
  3. Store thread references in another list
  4. Join all threads to wait for completion

This pattern scales easily - add more URLs, get more concurrent downloads!

httpbin.org:
------------
httpbin.org is a free HTTP testing service. We use it to download sample
images without needing to set up our own server or use real file hosts.

=============================================================================
"""

import threading  # For creating concurrent threads
import requests   # Popular HTTP library for making web requests (pip install requests)
import time       # For measuring execution time


def download(url):
    """
    Downloads content from a given URL.
    
    This function demonstrates a classic I/O-BOUND operation:
      - CPU work: minimal (just processing the response)
      - Waiting time: high (network latency, server response, data transfer)
    
    During the network wait, the GIL is RELEASED, allowing other threads
    to make their own requests simultaneously!
    
    Args:
        url (str): The URL to download from
    
    Note on requests library:
    -------------------------
    requests.get(url) makes an HTTP GET request and returns a Response object.
    - resp.content: The raw bytes of the response body
    - resp.text: The response as a string (for text content)
    - resp.status_code: HTTP status code (200 = success)
    - resp.headers: Response headers as a dictionary
    """
    print(f"📥 Starting download from {url}")
    
    # Make HTTP GET request - THIS IS WHERE THE WAITING HAPPENS
    # While waiting for the server response, Python releases the GIL
    # Other threads can run during this time!
    resp = requests.get(url)
    
    # len(resp.content) gives us the size of downloaded data in bytes
    print(f"✅ Finished downloading from {url}, size: {len(resp.content)} bytes")


# =============================================================================
# LIST OF URLS TO DOWNLOAD
# =============================================================================
# httpbin.org provides test endpoints that return sample images
# These are small images, perfect for demonstrating concurrent downloads

urls = [
    "https://httpbin.org/image/jpeg",  # Returns a JPEG image
    "https://httpbin.org/image/png",   # Returns a PNG image
    "https://httpbin.org/image/svg",   # Returns an SVG image
]


# =============================================================================
# CONCURRENT DOWNLOAD PATTERN
# =============================================================================
# This is a COMMON PATTERN for handling multiple I/O-bound tasks:
#   1. Create a list to store thread references
#   2. Loop through tasks, creating and starting threads
#   3. Join all threads at the end

print("=" * 60)
print("🌐 CONCURRENT DOWNLOADER: Threading Demo")
print("=" * 60)
print(f"Downloading {len(urls)} files concurrently...\n")

start = time.time()

# List to keep track of all our threads
# We need this so we can .join() them later!
threads = []

# =============================================================================
# STEP 1: CREATE AND START THREADS IN A LOOP
# =============================================================================
# This pattern is more scalable than creating threads manually:
#   t1 = Thread(...), t2 = Thread(...), etc.
# With a loop, we can handle any number of URLs!

for url in urls:
    # Create a new thread for this download
    # args=(url,) - Remember: single-element tuple needs trailing comma!
    t = threading.Thread(target=download, args=(url,))
    
    # Start the thread immediately
    # All downloads begin at (almost) the same time!
    t.start()
    
    # Save the thread reference so we can join it later
    threads.append(t)

# At this point, all 3 downloads are happening CONCURRENTLY!
# The main thread continues immediately without waiting.


# =============================================================================
# STEP 2: WAIT FOR ALL THREADS TO COMPLETE
# =============================================================================
# We need a separate loop for joining because:
#   - If we joined inside the first loop, downloads would be SEQUENTIAL
#   - We want to START all threads first, THEN wait for all to finish

for t in threads:
    t.join()  # Wait for each thread to complete

# Only after ALL downloads are done, we continue

end = time.time()

print(f"\n🎉 All downloads done in {end - start:.2f} seconds!")


# =============================================================================
# EXPECTED OUTPUT
# =============================================================================
#
# ============================================================
# 🌐 CONCURRENT DOWNLOADER: Threading Demo
# ============================================================
# Downloading 3 files concurrently...
#
# 📥 Starting download from https://httpbin.org/image/jpeg
# 📥 Starting download from https://httpbin.org/image/png
# 📥 Starting download from https://httpbin.org/image/svg
# ✅ Finished downloading from https://httpbin.org/image/svg, size: 8090 bytes
# ✅ Finished downloading from https://httpbin.org/image/jpeg, size: 35588 bytes
# ✅ Finished downloading from https://httpbin.org/image/png, size: 8090 bytes
#
# 🎉 All downloads done in 0.85 seconds!
#
# Note: 
#   - All 3 "Starting" messages appear almost instantly (concurrent start)
#   - "Finished" messages appear in order of completion, not start order
#   - Total time ≈ slowest single download, NOT sum of all downloads
#
# =============================================================================

# =============================================================================
# WHY THIS WORKS: THE GIL AND NETWORK I/O
# =============================================================================
#
# When requests.get() is waiting for a server response:
#   1. It's not executing Python bytecode (just waiting)
#   2. Python releases the GIL during this wait
#   3. Other threads can acquire the GIL and make their requests
#   4. All requests happen "in parallel" from a timing perspective
#
# This is why threading is PERFECT for:
#   ✅ Web scraping multiple pages
#   ✅ Downloading multiple files
#   ✅ Making multiple API calls
#   ✅ Any network I/O operations
#
# =============================================================================

# =============================================================================
# COMMON MISTAKES TO AVOID
# =============================================================================
#
# ❌ WRONG: Joining inside the creation loop (makes it sequential!)
#
#     for url in urls:
#         t = threading.Thread(target=download, args=(url,))
#         t.start()
#         t.join()  # ❌ This waits for EACH thread before starting the next!
#
# ✅ CORRECT: Start all threads first, then join all threads
#
#     threads = []
#     for url in urls:
#         t = threading.Thread(target=download, args=(url,))
#         t.start()
#         threads.append(t)
#     
#     for t in threads:
#         t.join()
#
# =============================================================================

# =============================================================================
# PRODUCTION CONSIDERATIONS
# =============================================================================
#
# For production code, consider:
#
# 1. THREAD POOLS: Use concurrent.futures.ThreadPoolExecutor
#    - Limits maximum concurrent threads
#    - Reuses threads (less overhead)
#    - Cleaner API with context managers
#
#    from concurrent.futures import ThreadPoolExecutor
#    with ThreadPoolExecutor(max_workers=5) as executor:
#        executor.map(download, urls)
#
# 2. ERROR HANDLING: Wrap downloads in try/except
#    - Network requests can fail (timeouts, connection errors)
#    - Handle exceptions gracefully in each thread
#
# 3. RATE LIMITING: Don't overwhelm servers
#    - Add delays or limit concurrent connections
#    - Respect robots.txt and API rate limits
#
# =============================================================================