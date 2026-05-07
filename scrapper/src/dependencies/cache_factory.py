from cache import CacheManager
from config import settings


class CacheManagerFactory:
    """Синглтон CacheManager."""

    def __init__(self) -> None:
        self._cache_manager = None

    def get_cache_manager(self) -> None:
        """Инициализация CacheManager."""
        if self._cache_manager is None:
            self._cache_manager = CacheManager(settings.valkey_host, settings.valkey_port, settings.valkey_ttl)

        return self._cache_manager
    
cache_factory = CacheManagerFactory()

def get_cache_manager() -> CacheManager:
    """Получить cache manager."""
    return cache_factory.get_cache_manager()
