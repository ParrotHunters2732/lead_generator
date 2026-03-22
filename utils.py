from models import BusinessInsightData , BusinessListData
from scraper.yellowpages import YellowPagesScraper
from fetchers.api import GetGekcoApi
from database.supabase import ReadData , WriteData
from dotenv import load_dotenv
import os
import time

load_dotenv()
stored_address = os.getenv('DATABASE_ADDRESS')
stored_password = os.getenv('DATABASE_PASSWORD')
stored_CGK_API_KEY = os.getenv('COINGEKCO_API_KEY')