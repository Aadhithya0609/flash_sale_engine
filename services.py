import redis.asyncio as redis  # <--- Note the .asyncio import
from contextlib import asynccontextmanager

# Connect to Redis using the Async client
# We use the same host/port as before
r = redis.Redis(host='localhost', port=6379, db=0)

@asynccontextmanager
async def redis_lock(lock_name, timeout=20): # Increased timeout for safety
    """
    Async Lock Manager.
    Instead of pausing the server, it 'awaits' the lock.
    """
    # Create the lock
    lock = r.lock(lock_name, timeout=timeout)
    
    # Acquire the lock asynchronously
    # blocking_timeout defines how long to wait for the lock before giving up
    acquired = await lock.acquire(blocking=True, blocking_timeout=10)
    
    if not acquired:
        raise Exception(f"Could not acquire lock for {lock_name}")
        
    try:
        yield acquired
    finally:
        # Always release!
        await lock.release()