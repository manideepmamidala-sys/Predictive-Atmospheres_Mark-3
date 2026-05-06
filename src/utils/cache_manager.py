"""
Cache Manager
Centralized caching for expensive computations.

Works with both Streamlit caching (@st.cache_data) and standalone
(could be used from Rhino or other environments).

Usage:
    from src.utils.cache_manager import CacheManager, cached

    # Decorator approach
    @cached('data')
    def load_expensive_data(path):
        return pd.read_csv(path)

    # Manual approach
    cache = CacheManager()
    data = cache.get_or_compute('key', expensive_function, *args)
"""
from functools import wraps, lru_cache
from typing import Callable, Any, Optional, Dict
import hashlib
import pickle
import os
import numpy as np

from src.config import get_config


def _get_streamlit():
    """Lazy import streamlit to avoid import errors in non-Streamlit environments."""
    try:
        import streamlit as st
        return st
    except ImportError:
        return None


def _generate_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(cache_type: str = 'data', ttl: Optional[int] = None):
    """
    Decorator for caching function results.

    Automatically uses Streamlit caching when available, falls back
    to lru_cache for standalone use.

    Args:
        cache_type: 'data' for data caching, 'resource' for resource caching
        ttl: Time-to-live in seconds (only for Streamlit)

    Usage:
        @cached('data', ttl=3600)
        def load_data(path):
            return pd.read_csv(path)
    """
    def decorator(func: Callable) -> Callable:
        st = _get_streamlit()

        if st is not None:
            # Use Streamlit caching
            if cache_type == 'resource':
                cache_decorator = st.cache_resource(ttl=ttl)
            else:
                cache_decorator = st.cache_data(ttl=ttl)
            return cache_decorator(func)
        else:
            # Fall back to lru_cache for non-Streamlit environments
            return lru_cache(maxsize=128)(func)

    return decorator


class CacheManager:
    """
    Centralized cache manager for expensive computations.

    Provides both automatic caching via decorators and manual caching
    via get_or_compute pattern.

    Example:
        cache = CacheManager()

        # Manual caching
        result = cache.get_or_compute(
            'expensive_calc_key',
            expensive_function,
            arg1, arg2,
            use_disk=True
        )

        # Clear specific cache
        cache.clear('expensive_calc_key')
    """

    def __init__(self, use_disk: bool = False, cache_dir: Optional[str] = None):
        """
        Initialize cache manager.

        Args:
            use_disk: Whether to persist cache to disk
            cache_dir: Directory for disk cache
        """
        self._config = get_config()
        self._memory_cache: Dict[str, Any] = {}
        self._use_disk = use_disk
        self._cache_dir = cache_dir or self._config.paths.cache_dir

        if use_disk and not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir, exist_ok=True)

    def get_or_compute(
        self,
        key: str,
        compute_func: Callable,
        *args,
        use_disk: Optional[bool] = None,
        **kwargs
    ) -> Any:
        """
        Get cached value or compute if not present.

        Args:
            key: Cache key
            compute_func: Function to compute value if not cached
            *args: Arguments for compute_func
            use_disk: Override for disk caching
            **kwargs: Keyword arguments for compute_func

        Returns:
            Cached or computed value
        """
        use_disk = use_disk if use_disk is not None else self._use_disk

        # Check memory cache first
        if key in self._memory_cache:
            return self._memory_cache[key]

        # Check disk cache if enabled
        if use_disk:
            disk_path = self._get_disk_path(key)
            if os.path.exists(disk_path):
                try:
                    with open(disk_path, 'rb') as f:
                        value = pickle.load(f)
                    self._memory_cache[key] = value
                    return value
                except Exception:
                    pass

        # Compute value
        value = compute_func(*args, **kwargs)

        # Store in cache
        self._memory_cache[key] = value

        if use_disk:
            try:
                with open(self._get_disk_path(key), 'wb') as f:
                    pickle.dump(value, f)
            except Exception:
                pass

        return value

    def _get_disk_path(self, key: str) -> str:
        """Get disk cache file path for a key."""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self._cache_dir, f"{safe_key}.cache")

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache.

        Args:
            key: Specific key to clear, or None to clear all
        """
        if key is None:
            self._memory_cache.clear()
        elif key in self._memory_cache:
            del self._memory_cache[key]

        if self._use_disk:
            if key is None:
                # Clear all disk cache
                for f in os.listdir(self._cache_dir):
                    if f.endswith('.cache'):
                        os.remove(os.path.join(self._cache_dir, f))
            else:
                disk_path = self._get_disk_path(key)
                if os.path.exists(disk_path):
                    os.remove(disk_path)


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        config = get_config()
        _cache_manager = CacheManager(use_disk=True)
    return _cache_manager