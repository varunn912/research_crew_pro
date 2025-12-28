import time
from functools import wraps
from collections import defaultdict
import threading
from typing import Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from openai import RateLimitError

class RateLimiter:
    """Thread-safe rate limiter with exponential backoff."""
    
    def __init__(self, max_calls: int = 3, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with self.lock:
                now = time.time()
                key = func.__name__
                
                # Remove old calls outside time window
                self.calls[key] = [
                    call_time for call_time in self.calls[key]
                    if now - call_time < self.time_window
                ]
                
                # Check if we can make the call
                if len(self.calls[key]) >= self.max_calls:
                    sleep_time = self.time_window - (now - self.calls[key][0]) + 1
                    print(f"⏳ Rate limit reached. Waiting {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                    self.calls[key] = []
                
                # Record this call
                self.calls[key].append(time.time())
            
            return func(*args, **kwargs)
        
        return wrapper

def retry_with_exponential_backoff(
    max_attempts: int = 5,
    initial_wait: int = 1,
    max_wait: int = 60
):
    """Decorator for exponential backoff retry."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=initial_wait, max=max_wait),
        retry=retry_if_exception_type((RateLimitError, Exception)),
        reraise=True
    )