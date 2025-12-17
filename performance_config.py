"""
Performance configuration for Juice Shop Solver
Adjust these settings to optimize execution speed
"""

# HTTP Request Settings
REQUEST_TIMEOUT = 5  # seconds - reduced from default 30s
MAX_RETRIES = 1  # Only retry once on failure
CONCURRENT_REQUESTS = 10  # Number of parallel requests

# Browser Settings
BROWSER_PAGE_LOAD_WAIT = 0.5  # seconds - reduced from 2-3s
BROWSER_ACTION_WAIT = 0.3  # seconds - reduced from 1s
BROWSER_IMPLICIT_WAIT = 3  # seconds for element finding

# Sleep/Wait Settings
ENABLE_SLEEPS = False  # Disable all optional sleeps for speed
MIN_SLEEP_TIME = 0.1  # Minimum sleep when needed

# Session Settings
USE_SESSION_POOLING = True  # Reuse HTTP sessions
SESSION_POOL_SIZE = 5

# Challenge Execution
RUN_PARALLEL = True  # Run independent challenges in parallel
SKIP_SCREENSHOTS = True  # Skip screenshot generation
SKIP_LOGGING = False  # Keep logging for debugging

# Advanced
USE_ASYNC = False  # Use asyncio (experimental)
AGGRESSIVE_MODE = True  # Maximum speed, may be unstable
