import os 
from dotenv import load_dotenv
import database.database as DBR
import fetchers.api as api
from scraper.yellopages import YelloPagesScraper 

load_dotenv()
stored_address = os.getenv('DATABASE_ADDRESS')
stored_password = os.getenv('DATABASE_PASSWORD')
stored_CGK_API_KEY = os.getenv('COINGEKCO_API_KEY')


