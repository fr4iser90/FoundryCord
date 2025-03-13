import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.shared.logging import logger

def create_http_client(retries=3, backoff_factor=0.3):
    session = requests.Session()
    
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Log the proxy settings
    logger.debug(f"HTTP Client Proxy Settings: {session.proxies}")
    
    return session

http_client = create_http_client()