"""
Caching service implementation with support for in-memory and Redis backends.

Provides a flexible caching service using the factory pattern:
- InMemoryCache: Thread-safe in-memory caching with TTL support and scheduled cleanup
- RedisCache: Redis-based caching with connection pooling

Note: InMemoryCache cleanup is handled by a scheduled job in main.jobs that runs every minute.

Usage:
    from main.lifespan import singletons
    cache = singletons.get('cache')

    # Set a value with 5-minute TTL
    await cache.set('key', 'value', ttl=300)

    # Get a value
    value = await cache.get('key')
"""

import asyncio
import fnmatch
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Optional, Union

from django.utils import timezone

from main import settings
from main.utils.logger import log


class BaseCacheService(ABC):
    """Abstract base class for cache service implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache by key."""
        pass

    @abstractmethod
    async def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Store a value in cache with optional TTL (in seconds or timedelta)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        pass

    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries. If pattern provided, clear matching keys only."""
        pass

    @abstractmethod
    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Retrieve multiple values from cache."""
        pass

    @abstractmethod
    async def set_many(
            self,
            mapping: dict[str, Any],
            ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Store multiple key-value pairs in cache."""
        pass

    @abstractmethod
    async def ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a key in seconds. Returns None if key doesn't exist or has no TTL."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connections and cleanup resources."""
        pass


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""
    value: Any
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None: return False
        return timezone.now() >= self.expires_at


class InMemoryCache(BaseCacheService):
    """Thread-safe in-memory cache implementation with TTL support."""

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        log.info("InMemoryCache initialized")

    def cleanup_expired(self):
        """Synchronous cleanup of expired entries. Called by scheduled job."""
        try:
            # Use a list to collect keys to avoid RuntimeError from dict size change during iteration
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                log.debug(f"InMemoryCache: Cleaned up {len(expired_keys)} expired entries")
        except Exception as e:
            log.error(f"Error in cache cleanup: {e}", exc_info=True)

    def _calculate_expiry(self, ttl: Optional[Union[int, timedelta]]) -> Optional[datetime]:
        """Calculate expiry datetime from TTL."""
        if ttl is None:
            return None
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        return timezone.now() + timedelta(seconds=ttl)

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.value

    async def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Store a value in cache with optional TTL."""
        try:
            async with self._lock:
                expires_at = self._calculate_expiry(ttl)
                self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            return True
        except Exception as e:
            log.error(f"Error setting cache key {key}: {e}", exc_info=True)
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None: return False
            if entry.is_expired():
                del self._cache[key]
                return False
            return True

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching pattern."""
        async with self._lock:
            if pattern is None:
                count = len(self._cache)
                self._cache.clear()
                return count

            # Simple pattern matching with wildcards
            keys_to_delete = [
                key for key in self._cache.keys()
                if fnmatch.fnmatch(key, pattern)
            ]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Retrieve multiple values from cache."""
        result = {}
        async with self._lock:
            for key in keys:
                entry = self._cache.get(key)
                if entry and not entry.is_expired():
                    result[key] = entry.value
                elif entry and entry.is_expired():
                    del self._cache[key]
        return result

    async def set_many(
            self,
            mapping: dict[str, Any],
            ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Store multiple key-value pairs in cache."""
        try:
            expires_at = self._calculate_expiry(ttl)
            async with self._lock:
                for key, value in mapping.items():
                    self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            return True
        except Exception as e:
            log.error(f"Error setting multiple cache keys: {e}", exc_info=True)
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a key in seconds."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None or entry.expires_at is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            remaining = (entry.expires_at - timezone.now()).total_seconds()
            return int(remaining) if remaining > 0 else 0

    async def close(self) -> None:
        """Cleanup resources."""
        self._cache.clear()
        log.info("InMemoryCache closed")


class RedisCache(BaseCacheService):
    """Redis-based cache implementation with connection pooling."""

    def __init__(
            self,
            host: str = 'localhost',
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None,
            max_connections: int = 10,
            socket_timeout: int = 5,
            socket_connect_timeout: int = 5,
            decode_responses: bool = False,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password

        try:
            # Imported here to avoid import errors if redis is not installed
            import redis.asyncio as redis
            from redis.asyncio.connection import ConnectionPool
        except ImportError:
            raise ImportError(
                "redis package is required for RedisCache. "
                "Install it with: pip install redis[hiredis]>=5.0.0"
            )

        # Create connection pool
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=decode_responses,
        )

        self.client: Optional[Any] = None
        self._initialized = False
        self._redis = redis
        log.info(f"RedisCache configured for {host}:{port}/{db}")

    async def _ensure_connection(self):
        """Ensure Redis connection is established."""
        if self.client is None:
            self.client = self._redis.Redis(connection_pool=self.pool)
            # Test connection
            try:
                await self.client.ping()
                self._initialized = True
                log.info("RedisCache connection established")
            except Exception as e:
                log.error(f"Failed to connect to Redis: {e}", exc_info=True)
                raise
        return self.client

    def _serialize(self, value: Any) -> bytes:
        """Serialize value using pickle."""
        return pickle.dumps(value)

    def _deserialize(self, value: Optional[bytes]) -> Optional[Any]:
        """Deserialize value using pickle."""
        if value is None: return None
        try:
            return pickle.loads(value)
        except Exception as e:
            log.error(f"Error deserializing cache value: {e}", exc_info=True)
            return None

    def _normalize_ttl(self, ttl: Optional[Union[int, timedelta]]) -> Optional[int]:
        """Normalize TTL to integer seconds."""
        if ttl is None:
            return None
        if isinstance(ttl, timedelta):
            return int(ttl.total_seconds())
        return ttl

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from Redis cache."""
        try:
            client = await self._ensure_connection()
            value = await client.get(key)
            return self._deserialize(value)
        except Exception as e:
            log.error(f"Redis error getting key {key}: {e}", exc_info=True)
            return None

    async def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Store a value in Redis cache with optional TTL."""
        try:
            client = await self._ensure_connection()
            serialized = self._serialize(value)
            ttl_seconds = self._normalize_ttl(ttl)

            if ttl_seconds:
                await client.setex(key, ttl_seconds, serialized)
            else:
                await client.set(key, serialized)
            return True
        except Exception as e:
            log.error(f"Redis error setting key {key}: {e}", exc_info=True)
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis cache."""
        try:
            client = await self._ensure_connection()
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            log.error(f"Redis error deleting key {key}: {e}", exc_info=True)
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis cache."""
        try:
            client = await self._ensure_connection()
            result = await client.exists(key)
            return result > 0
        except Exception as e:
            log.error(f"Redis error checking key {key}: {e}", exc_info=True)
            return False

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear Redis cache entries matching pattern."""
        try:
            client = await self._ensure_connection()

            if pattern is None:
                # Clear all keys in current database
                await client.flushdb()
                return -1  # Return -1 to indicate all keys cleared

            # Use SCAN to find matching keys
            count = 0
            async for key in client.scan_iter(match=pattern, count=100):
                await client.delete(key)
                count += 1
            return count
        except Exception as e:
            log.error(f"Redis error clearing cache: {e}", exc_info=True)
            return 0

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Retrieve multiple values from Redis cache."""
        try:
            client = await self._ensure_connection()
            values = await client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    deserialized = self._deserialize(value)
                    if deserialized is not None:
                        result[key] = deserialized
            return result
        except Exception as e:
            log.error(f"Redis error getting multiple keys: {e}", exc_info=True)
            return {}

    async def set_many(
            self,
            mapping: dict[str, Any],
            ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Store multiple key-value pairs in Redis cache."""
        try:
            client = await self._ensure_connection()

            # Serialize all values
            serialized_mapping = {
                key: self._serialize(value)
                for key, value in mapping.items()
            }

            # Use pipeline for efficiency
            async with client.pipeline() as pipe:
                if ttl:
                    ttl_seconds = self._normalize_ttl(ttl)
                    for key, value in serialized_mapping.items():
                        pipe.setex(key, ttl_seconds, value)
                else:
                    pipe.mset(serialized_mapping)
                await pipe.execute()

            return True
        except Exception as e:
            log.error(f"Redis error setting multiple keys: {e}", exc_info=True)
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a key in seconds."""
        try:
            client = await self._ensure_connection()
            result = await client.ttl(key)
            # Redis returns -2 if key doesn't exist, -1 if no expiry
            if result == -2:
                return None  # Key doesn't exist
            if result == -1:
                return None  # No expiry set
            return result
        except Exception as e:
            log.error(f"Redis error getting TTL for key {key}: {e}", exc_info=True)
            return None

    async def close(self) -> None:
        """Close Redis connections."""
        if self.client:
            await self.client.aclose()
            self.client = None
        await self.pool.aclose()
        log.info("RedisCache connection closed")


@lru_cache()
def get_cache_service() -> BaseCacheService:
    """
    Factory function to create and return the appropriate cache service.
    Uses @lru_cache to ensure singleton pattern.

    Attempts to initialize configured cache service with fallback to in-memory
    if Redis connection fails.
    """
    from main import settings

    cache_type = settings.CACHE_SERVICE.lower()

    if cache_type == 'redis':
        try:
            log.info("Attempting to initialize Redis cache...")
            cache = RedisCache(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT,
            )
            # Note: Connection is tested lazily on first use
            log.info("Redis cache service created successfully")
            return cache
        except Exception as e:
            log.error(
                f"Failed to initialize Redis cache: {e}. Falling back to in-memory cache.",
                exc_info=True
            )
            # Fallback to in-memory
            return InMemoryCache()

    elif cache_type == 'inmem':
        log.info("Initializing in-memory cache...")
        return InMemoryCache()

    else:
        log.warning(
            f"Unknown cache service type '{cache_type}'. Defaulting to in-memory cache."
        )
        return InMemoryCache()


async def initialize_cache_service() -> BaseCacheService:
    """
    Initialize the cache service during application startup.
    This should be called from the lifespan context manager.

    For InMemoryCache: Cleanup is handled by scheduled job in main.jobs
    For RedisCache: Tests connection and logs any errors

    Returns the initialized cache service.
    """
    cache = get_cache_service()

    # Perform initialization based on cache type
    if isinstance(cache, RedisCache):
        try:
            # Test connection by attempting to ping
            await cache._ensure_connection()
            log.info("Redis connection verified")
        except Exception as e:
            log.error(
                f"Redis connection test failed: {e}. "
                "Cache operations will fail until Redis is available.",
                exc_info=True
            )

    # set default cache stores
    for store in settings.DEFAULT_CACHE_STORES:
        if not await cache.get(store): await cache.set(store, {})

    return cache


async def shutdown_cache_service(cache: BaseCacheService) -> None:
    """
    Shutdown the cache service during application shutdown.
    This should be called from the lifespan context manager.
    """
    try:
        await cache.close()
        log.info("Cache service shut down successfully")
    except Exception as e:
        log.error(f"Error shutting down cache service: {e}", exc_info=True)
