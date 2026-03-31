from decorators import timer_count , exception_handler
from scraper.yellowpages import YellowPagesScraper
from database.supabase import Writer , Reader
from time import sleep
from models import ConfigJson
from random import uniform
import requests
import logging


logging.basicConfig(
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
    )
logger = logging.getLogger(__name__)

with open('config.json', 'r') as f:
    try:
        confirmed_config_data = ConfigJson.model_validate_json(f.read()).model_dump()
    except Exception as e:
        logger.critical(f"The config is incompatible, change data in 'config.json': {e}")
        raise SystemExit(1)

@exception_handler
@timer_count
def store_business_list(location:list|str ,category: list|str)->list:
    logging.info(f" utils.py | {store_business_list.__name__} | Execute ({confirmed_config_data["page_per_request"]})page/s")
    error_list = []
    with requests.Session() as session:
        for i , v  in enumerate(range(0,confirmed_config_data["page_per_request"]),start=1):
            logger.info(f" utils.py | {store_business_list.__name__} | page: {i}/{confirmed_config_data["page_per_request"]}")
            pick_float = uniform(
            confirmed_config_data["rate_min"],
            confirmed_config_data["rate_max"]
            )
            logger.info(f" utils.py | {store_business_list.__name__} | {pick_float:.1f}s")
            sleep(pick_float)
            data = YellowPagesScraper().get_business_list(
                category,
                location,
                page=i,
                session=session,
                attempt=confirmed_config_data["max_attempt"]
                )
            if data == 404:
                return None
            elif data and not data == 404:
                Writer().write_business_list(business_list_data=data)
                continue
            else:
                logger.info(f" utils.py | {store_business_list.__name__} | Unsuccessful to write business list")
                error_list.append(i)
                continue
        logger.info(f" utils.py | {store_business_list.__name__} | failed page/s: {error_list}")
        if confirmed_config_data["redo_on_fail_page"] and error_list:
                for _ in range(confirmed_config_data["redo_on_fail_page_attempt"]):
                    if error_list:
                        still_failed = []
                        for num in error_list:
                            pick_float = uniform(
                            confirmed_config_data["rate_min"],
                            confirmed_config_data["rate_max"]
                            )
                            logger.info(f" utils.py | {store_business_list.__name__} (redo) | row: {num}/{error_list}")
                            logger.info(f" utils.py | {store_business_list.__name__} (redo) | {pick_float:.1f}s")
                            sleep(pick_float)
                            result_redo = YellowPagesScraper().get_business_list(
                                category,
                                location,
                                page=num,
                                session=session,
                                attempt=confirmed_config_data["max_attempt"]
                            )
                            if result_redo == 404:
                                return None
                            elif result_redo and not result_redo != 404:
                                Writer().write_business_list(business_list_data=result_redo)
                            else:
                                logger.info(f" utils.py | {store_business_list.__name__} (redo) | Unsuccessful to write business list")
                                still_failed.append(num)
                        error_list = still_failed
                        sleep(confirmed_config_data["redo_on_fail_page_attempt"])
                    else:
                        break
                    

@exception_handler
@timer_count
def store_business_insight()->None:
    null_business_list = Reader().get_url_and_unique_key(confirmed_config_data["amount_write_business_insight"])
    if not null_business_list:
        logger.info(f" utils.py | {store_business_insight.__name__} | No 'Null' data to operated on!")
    else:
        logger.info(f" utils.py | {store_business_insight.__name__} |  Execute ({len(null_business_list)})row/s")
        error_list = [] 
        with requests.Session() as session:
            for i , v in enumerate(null_business_list):
                pick_float = uniform(
                confirmed_config_data["rate_min"],
                confirmed_config_data["rate_max"]
                )
                logger.info(f" utils.py | {store_business_insight.__name__} | row: {i+1}/{len(null_business_list)}")
                logger.info(f" utils.py | {store_business_insight.__name__} | {pick_float:.1f}s")
                sleep(pick_float) 
                result = YellowPagesScraper().get_business_insight(
                target_url=v[0],session=session,
                attempt=confirmed_config_data["max_attempt"])
                if result:
                    Writer().write_business_insight(dict_business_insight=result,unique_key=v[1])
                else:
                    logger.info(f" utils.py | {store_business_insight.__name__} | Unsuccessful to write business list")
                    error_list.append((i+1,v))
            logger.info(f" utils.py | {store_business_insight.__name__} | failed page/s: {[i for i,_ in error_list]}")
            
            if confirmed_config_data["redo_on_fail_page"] and error_list:
                for _ in range(confirmed_config_data["redo_on_fail_page_attempt"]):
                    if error_list:
                        still_failed = []
                        for num , url_unq in error_list:
                            pick_float = uniform(confirmed_config_data["rate_min"],confirmed_config_data["rate_max"])
                            logger.info(f" utils.py | {store_business_insight.__name__} (redo) | row: {num}/{[i for i , _ in error_list]}")
                            logger.info(f" utils.py | {store_business_insight.__name__} (redo) | {pick_float:.1f}s")
                            sleep(pick_float)
                            result_redo = YellowPagesScraper().get_business_insight(
                            target_url=url_unq[0],
                            session=session,
                            attempt=confirmed_config_data["max_attempt"]
                            )
                            if result_redo:
                                Writer().write_business_insight(
                                dict_business_insight=result_redo,
                                unique_key=url_unq[1]
                                )
                            else:
                                logger.info(f" utils.py | {store_business_insight.__name__} (redo) | Unsuccessful to write business list")
                                still_failed.append(
                                    (num,url_unq)
                                    )
                        error_list = still_failed
                        sleep(confirmed_config_data["redo_on_fail_page_attempt"])
                    else:
                        break
            return
    