from scraper.yellowpages import YellowPagesScraper
from database.supabase import Writer
from models import ConfigJson
from time import sleep
from random import uniform
import logging
import requests

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
    
def store_business_list():
    logging.info("executing 'store_business_list'")
    yellow_object = YellowPagesScraper()
    error_list = []
    with requests.Session() as session:
        for i , v  in enumerate(range(0,confirmed_config_data["page_per_request"]),start=1):
            logger.info(f"store_business_list | 'utils.py' | page: {i}")
            data = yellow_object.get_business_list(
                max_attempt=confirmed_config_data["max_attempt"], 
                attempt_duration=confirmed_config_data["attempt_duration"], 
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
        logger.info("execution of 'store_business_list' completed")
        logger.info(f"store_business_list | 'utils.py' | failed page/s: {error_list}")

    
    
    
    

