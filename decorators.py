from functools import wraps
from time import perf_counter
from logs.log import CustomLogger
from requests import HTTPError , Timeout , ConnectionError
from psycopg2 import ProgrammingError , OperationalError , IntegrityError , Error
import os
import inspect

logger = CustomLogger().get_logger(__name__)

def timer_count(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        start = perf_counter()
        file_path = inspect.getfile(fn)
        result = fn(*args,**kwargs)
        end = perf_counter()
        total_seconds = end-start
        if total_seconds > 60 < 3200:
            min , sec = divmod(total_seconds,60)
            logger.info(f"{os.path.basename(file_path)} | {fn.__name__} | Completed in {min:.0f}:{sec:.0f}s")
        elif total_seconds > 3600:
            min , sec = divmod(total_seconds,60)
            hour , min = divmod(min,60) 
            logger.info(f"{os.path.basename(file_path)} | {fn.__name__} | Completed in {hour:.0f}:{min:.0f}:{sec:.2f}s")
        else:
            logger.info(f"{os.path.basename(file_path)} | {fn.__name__} | Completed in {total_seconds:.2f}s")
        return result
    return wrapper

def basic_exception_handling(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        result = None
        file_path = inspect.getfile(fn)
        try:
            result = fn(*args,**kwargs)
        except ( HTTPError , ConnectionError , Timeout ) as e:
            logger.error(f"{os.path.basename(file_path)} | {fn.__name__} | Network_failed | :  {e}")
        except ( ProgrammingError , OperationalError , IntegrityError , Error ) as e:
            logger.critical(f"{os.path.basename(file_path)} | {fn.__name__} | Database_failed | : {e}")
            raise SystemExit(1)
        except Exception as e:
            logger.critical(f"{os.path.basename(file_path)} | {fn.__name__} | Unexpected | : {e}")
            raise e 
        return result
    return wrapper

