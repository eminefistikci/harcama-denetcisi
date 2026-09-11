import time
import sys
from functools import wraps
import datetime

def measure_runtime(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"{func.__name__} Execution time: {duration} seconds", file=sys.stderr) 
        return result
    return decorator

def audit_action(action_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Action {action_name} started. ",file =sys.stderr)
            result = fn(*args, **kwargs)
            print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Action {action_name} completed. ",file =sys.stderr)
            return result
        return wrapper
    return decorator
