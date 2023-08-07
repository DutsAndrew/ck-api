import cachetools

token_cache = cachetools.TTLCache(maxsize=100, ttl=60 * 60)