import time
from functools import wraps
from logger import logger

def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, max_attempts=20):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            t = start_sleep_time
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"Exceeded maximum attempts for {func.__name__}")
                        raise
                    if t < border_sleep_time:
                        t = min(t * factor, border_sleep_time)
                    logger.info(f"Retrying {func.__name__} in {t} seconds (Attempt {attempts}/{max_attempts})")
                    time.sleep(t)
        return inner
    return func_wrapper