import time
import requests
from bs4 import BeautifulSoup
from django.core.cache import caches
from django.core.exceptions import SuspiciousOperation
from celery import shared_task
import logging
import traceback
from django.conf import settings
from functools import wraps

from .providers import get_provider
from .repository import PriceRepository

# Setup logging
logger = logging.getLogger(__name__)

# Get default provider name from settings or use 'tgju' as default
DEFAULT_PROVIDER = getattr(settings, 'GOLD_PRICE_PROVIDER', 'tgju')

# Cache storage
_price_cache = {
    'value': None,
    'timestamp': 0,
    'provider': None
}

def _get_gold_price_from_redis(provider_name):
    """
    Internal function to get gold price from Redis.
    """
    try:
        repository = PriceRepository(provider_name=provider_name)
        return repository.get_price()
    except SuspiciousOperation as e:
        logger.warning(f"Could not get gold price: {str(e)}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error getting gold price: {str(e)}")
        return 0

def get_gold_price(provider_name=None):
    """
    Get gold price with local memory caching.
    
    Args:
        provider_name (str, optional): Name of the provider to use.
                                      If None, uses the default provider from settings.
                                      
    Returns:
        int: Gold price
    """
    if provider_name is None:
        provider_name = DEFAULT_PROVIDER
    
    current_time = time.time()
    cache_ttl = 5  # 5 seconds TTL
    
    # Check if we have a valid cached value
    if (_price_cache['value'] is not None and 
        _price_cache['provider'] == provider_name and
        current_time - _price_cache['timestamp'] < cache_ttl):
        return _price_cache['value']
    
    # Get fresh value from Redis
    price = _get_gold_price_from_redis(provider_name)
    
    # Update cache
    _price_cache.update({
        'value': price,
        'timestamp': current_time,
        'provider': provider_name
    })
    
    return price

@shared_task
def update_gold_price(provider_name=None):
    """
    Periodic task to update gold price in Redis.
    
    Args:
        provider_name (str, optional): Name of the provider to use. 
                                      If None, uses the default provider from settings.
                                      
    Returns:
        bool: True if successful, False otherwise
    """
    if provider_name is None:
        provider_name = DEFAULT_PROVIDER
    
    logger.info(f"Starting gold price update from {provider_name}")
    
    try:
        # Get provider instance
        provider = get_provider(provider_name)
        logger.debug(f"Using provider: {provider.name}")
        
        # Get repository for the provider
        repository = PriceRepository(provider_name=provider_name)
        
        # Get price from provider
        try:
            price, timestamp = provider.get_price()
            logger.info(f"Retrieved price: {price}, timestamp: {timestamp}")
            
            if price is None or timestamp is None:
                logger.error(f"Provider {provider_name} returned None for price or timestamp")
                return False
                
        except Exception as e:
            logger.error(f"Error getting price from {provider_name}: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
        
        # Save price to repository
        try:
            success = repository.save_price(price, timestamp)
            if success:
                logger.info(f"Successfully updated gold price from {provider_name}: {price}")
            else:
                logger.error(f"Failed to save gold price from {provider_name}")
            return success
        except Exception as e:
            logger.error(f"Error saving gold price: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"Error updating gold price from {provider_name}: {str(e)}")
        logger.debug(traceback.format_exc())
        return False