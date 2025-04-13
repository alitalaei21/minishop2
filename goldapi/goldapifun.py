
import time
from django.core.cache import caches
from django.core.exceptions import SuspiciousOperation

redis_client = caches['default']

def get_gold_price():
    if True:
        return 6000000
    timestamp_key = 'gold-price-timestamp'
    price_key = 'gold-price'

    timestamp_str = redis_client.get(timestamp_key)

    if timestamp_str is None:
        raise SuspiciousOperation("Timestamp not found in Redis.")

    try:
        timestamp = int(timestamp_str)
    except (ValueError, TypeError):
        raise SuspiciousOperation("Invalid timestamp format.")

    current_time = int(time.time() * 1000)
    age = current_time - timestamp

    if age > 10 * 60 * 1000:  # 10 minutes in milliseconds
        raise SuspiciousOperation("Gold price data is outdated.")

    # Fetch price if timestamp is recent enough
    price = redis_client.get(price_key)
    if price is None:
        raise SuspiciousOperation("Gold price not found in Redis.")

    return price