from scraper.yellowpages import YellowPagesScraper
from fetchers.api import GetGekcoApi
from database.supabase import Reader , Writer
from models import ConfigJson , ExportJson 
import time

with open('config.json', 'r') as f:
    try:
        confirmed_config_data = ConfigJson.model_validate_json(f.read()).model_dump()
    except Exception as e:
        raise e
    
def store_business_list():
    model = YellowPagesScraper("plumber" , "NYC" , "NY")
    yellow_object = model.get_business_list(max_attempt=confirmed_config_data["max_attempt"], attempt_duration=confirmed_config_data["attempt_duration"])
    if yellow_object:
        return yellow_object
    return yellow_object
    return print("process_failed")

