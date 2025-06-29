import time
import logging
from django.core.cache import caches
from django.core.exceptions import SuspiciousOperation
from django.conf import settings

logger = logging.getLogger(__name__)

class PriceRepository:
    """
    Repository class for storing and retrieving gold price data.
    Currently uses Redis as the storage backend.
    """
    
    def __init__(self, provider_name="tgju", cache_name="default"):
        """
        Initialize the repository.
        
        Args:
            provider_name (str): Name of the provider (used as a prefix for keys)
            cache_name (str): Name of the cache to use
        """
        self.provider_name = provider_name
        self.redis_client = caches[cache_name]
        self.price_key = f"{provider_name}-gold-price"
        self.timestamp_key = f"{provider_name}-gold-price-timestamp"
        # Get max age from settings or use default (30 minutes)
        self.max_age_ms = getattr(settings, 'GOLD_PRICE_MAX_AGE', 30 * 60 * 1000)
    
    def save_price(self, price, timestamp):
        """
        Save price and timestamp to Redis.
        
        Args:
            price (int): Gold price
            timestamp (int): Timestamp in milliseconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        if price is None or timestamp is None:
            logger.error(f"Cannot save null price or timestamp for {self.provider_name}")
            return False
            
        try:
            # Validate price and timestamp
            if not isinstance(price, (int, float)):
                logger.error(f"Invalid price type for {self.provider_name}: {type(price)}")
                return False
                
            if not isinstance(timestamp, (int, float)):
                logger.error(f"Invalid timestamp type for {self.provider_name}: {type(timestamp)}")
                return False

            logger.info('Saving to redis....')
            # Save to Redis
            # Here the exception is being thrown. What could be the reason?
            self.redis_client.set(self.price_key, str(price), 1800) #30 min
            self.redis_client.set(self.timestamp_key, str(timestamp), 1800) #30 min
            logger.info('Saved to rediszz')
            logger.info(f"Updated {self.provider_name} gold price: {price}, timestamp: {timestamp}")
            return True
        except Exception as e:
            logger.error(f"Error saving {self.provider_name} gold price: {str(e)}")
            return False
    
    def get_price(self):
        """
        Get gold price from Redis.
        
        Returns:
            int: Gold price
            
        Raises:
            SuspiciousOperation: If timestamp is missing, invalid, outdated, or price is missing
        """
        timestamp_str = self.redis_client.get(self.timestamp_key)
        
        if timestamp_str is None:
            raise SuspiciousOperation(f"Timestamp not found in Redis for provider {self.provider_name}.")
        
        try:
            timestamp = int(timestamp_str)
        except (ValueError, TypeError):
            raise SuspiciousOperation(f"Invalid timestamp format for provider {self.provider_name}.")
        
        current_time = int(time.time() * 1000)
        age = current_time - timestamp
        
        if age > self.max_age_ms:
            raise SuspiciousOperation(f"Gold price data is outdated for provider {self.provider_name}.")
        
        # Fetch price if timestamp is recent enough
        price = self.redis_client.get(self.price_key)
        if price is None:
            raise SuspiciousOperation(f"Gold price not found in Redis for provider {self.provider_name}.")
        
        return int(price) 