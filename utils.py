from scraper.yellowpages import YellowPagesScraper
from database.supabase import Writer , Reader
from time import sleep , perf_counter
from models import ConfigJson
from helper import get_time
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
    
def store_business_list()->None:
    logging.info("store_business_list | 'utils.py' | Execute")
    start_timer = perf_counter()
    error_list = []
    with requests.Session() as session:
        for i , v  in enumerate(range(0,confirmed_config_data["page_per_request"]),start=1):
            logger.info(f"store_business_list | 'utils.py' | page: {i}/{confirmed_config_data["page_per_request"]}")
            data = YellowPagesScraper().get_business_list( #get_business_list_returning dict
                category=confirmed_config_data["category"],
                location=confirmed_config_data["location"],
                page=i,
                session=session
                )    
            pick_float = uniform(confirmed_config_data["rate_min"],confirmed_config_data["rate_max"])
            logger.info(f"store_business_list | 'utils.py' | {pick_float:.1f}s")
            if data:
                Writer().write_business_list(business_list_data=data)
                sleep(pick_float)
                continue
            else:
                logger.info("store_business_list | 'utils.py' | Unsuccessful to write business list")
                error_list.append(i)
                sleep(pick_float)
                continue
        end_timer = perf_counter()
        logger.info(f"store_business_list | 'utils.py' | Completed ({get_time(start=start_timer,finish=end_timer):.2f}s)")
        logger.info(f"store_business_list | 'utils.py' | failed page/s: {error_list}")

def store_business_insight()->None:
    null_business_list = Reader().get_url_and_unique_key(confirmed_config_data["amount_write_business_insight"])
    if null_business_list:
        logger.info(f"store_business_insight | 'utils.py' | Execute ({len(null_business_list)})row/s")
        start_timer = perf_counter()
        error_list = []
        with requests.Session() as session:
            for i , v in enumerate(null_business_list):
                pick_float = uniform(confirmed_config_data["rate_min"],confirmed_config_data["rate_max"])
                logger.info(f"store_business_insight | 'utils.py' | page: {i+1}/{len(null_business_list)}")
                result = YellowPagesScraper().get_business_insight(target_url=v[0],session=session)
                if result:
                    Writer().write_business_insight(dict_business_insight=result,unique_key=v[1])
                    logger.info(f"store_business_insight | 'utils.py' | {pick_float:.1f}s")
                    sleep(pick_float)
                else:
                    logger.info("store_business_insight | 'utils.py' | Unsuccessful to write business list")
                    error_list.append(i)
                    logger.info(f"store_business_insight | 'utils.py' | {pick_float:.1f}s")
                    sleep(pick_float)
            end_timer = perf_counter()
            logger.info(f"store_business_insight | 'utils.py' | Completed2 ({get_time(start=start_timer,finish=end_timer):.2f}s)")
            logger.info(f"store_business_insight | 'utils.py' | failed page/s: {error_list}")
    else:
        logger.info("store_business_insight | 'utils.py' | No 'Null' data to operated on!")