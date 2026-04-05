from decorators import timer_count , basic_exception_handling
from scraper.yellowpages import YellowPagesScraper
from database.supabase import Writer , Reader
from time import sleep
from models import ConfigJson
from random import uniform
import requests
from logs.log import CustomLogger
from helpers import get_json_config_dict
from retry import retry_business_list_fail_pages, retry_business_insight_fail_pages

logger = CustomLogger().get_logger(__name__)


class GetAndStoreData:
    def __init__(self):
        confirmed_config_data = get_json_config_dict()
        self.page_per_request = confirmed_config_data["page_per_request"]
        self.rate_min = confirmed_config_data["rate_min"]
        self.rate_max = confirmed_config_data["rate_max"]
        self.max_attempt = confirmed_config_data["max_attempt"]
        self.attempt_duration = confirmed_config_data["attempt_duration"]
        self.write_business_insight_on_loop = confirmed_config_data["write_business_insight_on_loop"]
        self.write_business_insight_loop_cooldown = confirmed_config_data["write_business_insight_loop_cooldown"]
        self.redo_on_fail_page = confirmed_config_data["redo_on_fail_page"]
        self.redo_on_fail_page_attempt = confirmed_config_data["redo_on_fail_page_attempt"]
        self.cookies = confirmed_config_data["header"]["cookies_string"]
        self.amount_write_business_insight = confirmed_config_data["amount_write_business_insight"]

    @basic_exception_handling
    @timer_count
    def business_list(self: ConfigJson ,location:list|str ,category: list|str)->None:
        logger.info(f" utils.py | {GetAndStoreData.business_list.__name__} | Execute ({self.page_per_request})page/s")
        error_list = []
        with requests.Session() as session:
            for i , v  in enumerate(range(0,self.page_per_request),start=1):
                logger.info(f" utils.py | {GetAndStoreData.business_list.__name__} | page: {i}/{self.page_per_request}")
                pick_float = uniform(
                self.rate_min,
                self.rate_max
                )
                logger.info(f" utils.py | {GetAndStoreData.business_list.__name__} | {pick_float:.1f}s")
                sleep(pick_float)
                data = YellowPagesScraper().get_business_list(
                    category,
                    location,
                    page=i,
                    session=session,
                    attempt=self.max_attempt
                    )
                if data == 404:
                    logger.warning("Page Not Found!")
                    return None
                elif data and not data == 404:
                    Writer().write_business_list(business_list_data=data)
                    continue
                else:
                    logger.info(f" utils.py | {GetAndStoreData.business_list.__name__} | Unsuccessful to write business list")
                    error_list.append(i)
                    continue
            logger.info(f" utils.py | {GetAndStoreData.business_list.__name__} | failed page/s: {error_list}")
            if self.redo_on_fail_page and error_list:
                error_list = retry_business_list_fail_pages(error_list, self, category, location, session)
            return []
                        

    @basic_exception_handling
    @timer_count
    def store_business_insight(self)->None:
        null_business_list = Reader().get_url_and_unique_key(self.amount_write_business_insight)
        if not null_business_list:
            logger.info(f" utils.py | {GetAndStoreData.store_business_insight.__name__} | No 'Null' data to operated on!")
        else:
            logger.info(f" utils.py | {GetAndStoreData.store_business_insight.__name__} |  Execute ({len(null_business_list)})row/s")
            error_list = [] 
            with requests.Session() as session:
                for i , v in enumerate(null_business_list):
                    pick_float = uniform(
                    self.rate_min,
                    self.rate_max
                    )
                    logger.info(f" utils.py | {GetAndStoreData.store_business_insight.__name__} | row: {i+1}/{len(null_business_list)}")
                    logger.info(f" utils.py | {GetAndStoreData.store_business_insight.__name__} | {pick_float:.1f}s")
                    sleep(pick_float) 
                    result = YellowPagesScraper().get_business_insight(
                    target_url=v[0],session=session,
                    attempt=self.max_attempt)
                    if result:
                        Writer().write_business_insight(dict_business_insight=result,unique_key=v[1])
                    else:
                        logger.info(f" utils.py | {GetAndStoreData.store_business_insight.__name__} | Unsuccessful to write business list")
                        error_list.append((i+1,v))
                logger.info(f" utils.py | {GetAndStoreData.store_business_insight.__name__} | failed page/s: {[i for i,_ in error_list]}")

                if self.redo_on_fail_page and error_list:
                    error_list = retry_business_insight_fail_pages(error_list, self, session)
                return
