from functools import wraps
from time import perf_counter
from logs.log import CustomLogger
from requests import HTTPError , Timeout , ConnectionError
from psycopg2 import ProgrammingError , OperationalError , IntegrityError , Error
import os
import inspect
from typing import Literal

logger = CustomLogger().get_logger(__name__)

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
            raise e
        except Exception as e:
            logger.critical(f"{os.path.basename(file_path)} | {fn.__name__} | Unexpected | : {e}")
            raise e
        return result
    return wrapper

def database_context_manager(mode: Literal["display","hidden"] = "hidden"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args,**kwargs):
            conn = None
            file_path = inspect.getfile(fn)
            try:
                conn=self.db_pool.getconn()
                result = fn(self,conn,*args,**kwargs)
            except ( ProgrammingError , OperationalError , IntegrityError , Error ) as e:
                if conn: conn.rollback()
                logger.critical(f"{os.path.basename(file_path)} | {fn.__name__} | Database_failed | : {e}")
                raise e
            except Exception as e:

                if conn: conn.rollback()
                logger.critical(f"{os.path.basename(file_path)} | {fn.__name__} | Unexpected | : {e}")
                raise e 
            else:
                if conn:
                    conn.commit()
                    if mode == 'display':
                        logger.info(f"{os.path.basename(file_path)} | {fn.__name__} | Successfully Commited Data!")
            finally:
                if conn: 
                    self.db_pool.putconn(conn)
            return result
        return wrapper
    return decorator