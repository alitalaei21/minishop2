from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import logging 
import time

logger = logging.getLogger(__name__)

class PriceProvider(ABC):
    """
    Abstract base class for gold price providers.
    Implement this class to add new price data sources.
    """
    
    @abstractmethod
    def get_price(self):
        """
        Get the current gold price.
        Returns:
            tuple: (price_value, timestamp_ms) where price_value is an integer
                  and timestamp_ms is the current timestamp in milliseconds
        """
        pass
    
    @property
    @abstractmethod
    def name(self):
        """
        Get the name of the price provider.
        
        Returns:
            str: Provider name
        """
        pass


class TGJUGoldProvider(PriceProvider):
    """
    Gold price provider that fetches data from TGJU.org
    Based on the Kotlin implementation in TGJUGoldPrice.kt
    """
    
    def __init__(self):
        self.url = "https://www.tgju.org/profile/geram18"
        self.selector = '[data-col="info.last_trade.PDrCotVal"]'
    
    @property
    def name(self):
        return "tgju"
    
    def get_price(self):
        """
        Fetch gold price from TGJU website.
        
        Returns:
            tuple: (price_value, timestamp_ms)
        
        Raises:
            Exception: If price fetching fails
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch gold price. Status code: {response.status_code}")
                raise Exception(f"Failed to fetch gold price. Status code: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            price_element = soup.select_one(self.selector)
            
            if not price_element:
                logger.error("Price element not found in the HTML")
                raise Exception("Price element not found in the HTML")
            
            price_text = price_element.text.strip() if price_element.text else ""
            if not price_text:
                logger.error("Price text is empty")
                raise Exception("Price text is empty")
                
            # Parse price, removing commas and converting to integer
            try:
                price = int(price_text.replace(',', '')) // 10
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to parse price text '{price_text}': {str(e)}")
                raise Exception(f"Failed to parse price text: {str(e)}")
                
            timestamp = int(time.time() * 1000)
            logger.info(f"Successfully fetched gold price: {price}, timestamp: {timestamp}")
            return price, timestamp
            
        except Exception as e:
            logger.error(f"Error in TGJUGoldProvider: {str(e)}")
            raise


# Factory to get price provider instances
def get_provider(provider_name="tgju"):
    """
    Factory function to get a price provider instance.
    
    Args:
        provider_name (str): Name of the provider
        
    Returns:
        PriceProvider: Instance of a price provider
        
    Raises:
        ValueError: If provider_name is not supported
    """
    providers = {
        "tgju": TGJUGoldProvider,
        # Add more providers here as they are implemented
    }
    
    if provider_name not in providers:
        raise ValueError(f"Provider '{provider_name}' is not supported. Available providers: {', '.join(providers.keys())}")
    
    return providers[provider_name]() 