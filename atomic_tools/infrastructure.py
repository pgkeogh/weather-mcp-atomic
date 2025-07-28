# atomic_tools/infrastructure.py
"""
Infrastructure atomic tools for MCP server.
Provides generic system operations like secrets and caching.
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from services.key_vault_service import KeyVaultService
from security.allowlists import ALLOWED_SECRETS

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL
_cache_store: Dict[str, Dict[str, Any]] = {}

class InfrastructureTools:
    """Infrastructure atomic tools with dependency injection."""
    
    def __init__(self, key_vault_service: KeyVaultService):
        self.key_vault_service = key_vault_service
    
    async def get_secret(
        self, 
        secret_name: str, 
        vault_name: Optional[str] = None
    ) -> str:
        """
        Retrieve any secret from Azure Key Vault.
        
        Args:
            secret_name: Name of the secret to retrieve
            vault_name: Optional vault name (uses default if not provided)
        
        Returns:
            Secret value as string
        
        Security: Validates secret_name against allowlist
        """
        
        if secret_name not in ALLOWED_SECRETS:
            raise SecurityError(f"Access denied to secret: {secret_name}")
        
        try:
            logger.info("Retrieving secret: %s", secret_name)
            secret_value = await self.key_vault_service.get_secret(secret_name)
            logger.info("Successfully retrieved secret: %s", secret_name)
            return secret_value
            
        except Exception as e:
            logger.error("Failed to retrieve secret %s: %s", secret_name, e)
            raise RuntimeError(f"Secret retrieval failed: {secret_name}") from e
    
    async def cache_data(
        self, 
        key: str, 
        data: Dict[str, Any], 
        ttl_seconds: int = 300
    ) -> bool:
        """
        Cache data with expiration for performance optimization.
        
        Args:
            key: Cache key identifier
            data: Data to cache (must be JSON serializable)
            ttl_seconds: Time to live in seconds (default: 5 minutes)
        
        Returns:
            True if cached successfully
        """
        try:
            expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)
            
            _cache_store[key] = {
                "data": data,
                "expires_at": expiry_time,
                "cached_at": datetime.now()
            }
            
            logger.info("Cached data with key '%s', TTL: %d seconds", key, ttl_seconds)
            return True
            
        except Exception as e:
            logger.error("Failed to cache data for key '%s': %s", key, e)
            return False
    
    async def get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data if available and not expired.
        
        Args:
            key: Cache key identifier
        
        Returns:
            Cached data or None if not found/expired
        """
        try:
            if key not in _cache_store:
                logger.debug("Cache miss for key: %s", key)
                return None
            
            cache_entry = _cache_store[key]
            
            # Check if expired
            if datetime.now() > cache_entry["expires_at"]:
                logger.debug("Cache expired for key: %s", key)
                del _cache_store[key]
                return None
            
            logger.info("Cache hit for key: %s", key)
            return cache_entry["data"]
            
        except Exception as e:
            logger.error("Failed to retrieve cached data for key '%s': %s", key, e)
            return None
    
    async def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries, optionally by pattern.
        
        Args:
            pattern: Optional pattern to match keys (simple substring match)
        
        Returns:
            Number of entries cleared
        """
        try:
            if pattern is None:
                count = len(_cache_store)
                _cache_store.clear()
                logger.info("Cleared entire cache: %d entries", count)
                return count
            
            # Pattern-based clearing
            keys_to_remove = [k for k in _cache_store.keys() if pattern in k]
            count = len(keys_to_remove)
            
            for key in keys_to_remove:
                del _cache_store[key]
            
            logger.info("Cleared cache entries matching '%s': %d entries", pattern, count)
            return count
            
        except Exception as e:
            logger.error("Failed to clear cache: %s", e)
            return 0


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass