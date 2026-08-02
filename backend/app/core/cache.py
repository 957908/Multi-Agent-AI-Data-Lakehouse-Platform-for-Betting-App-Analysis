"""
File: cache.py
Purpose:
    In-memory TTL performance caching utility for high-throughput API endpoints.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import time
import functools
import logging
from typing import Dict, Tuple, Any, Callable

logger = logging.getLogger("backend.core.cache")


class SimpleTTLCache:
    """
    Thread-safe simple in-memory key-value cache with TTL expiration.
    """

    def __init__(self, default_ttl: int = 60):
        self._store: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Any:
        """Retrieves item from cache if not expired."""
        if key in self._store:
            val, expiry = self._store[key]
            if time.time() < expiry:
                return val
            # Expired
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Sets item in cache with TTL."""
        ttl_val = ttl if ttl is not None else self.default_ttl
        expiry = time.time() + ttl_val
        self._store[key] = (value, expiry)

    def clear(self) -> None:
        """Clears all cached items."""
        self._store.clear()


# Global cache instance
api_cache = SimpleTTLCache(default_ttl=60)


def cache_response(ttl_seconds: int = 60):
    """
    Decorator for caching function return values in memory.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Construct cache key from function name and str arguments
            key_parts = [func.__name__] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(key_parts)

            cached_val = api_cache.get(cache_key)
            if cached_val is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_val

            result = func(*args, **kwargs)
            api_cache.set(cache_key, result, ttl=ttl_seconds)
            return result
        return wrapper
    return decorator
