def cleanup_inmemory_cache():
    """Cleanup expired entries from in-memory cache."""
    from main.lifespan import singletons
    from main.utils.cache import InMemoryCache

    try:
        cache = singletons.get('cache')
        if isinstance(cache, InMemoryCache):
            cache.cleanup_expired()
    except Exception:
        # Cache may not be initialized yet during startup
        pass
