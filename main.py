import os 
from dotenv import load_dotenv
import database.database as DBR
import fetchers.api as api

load_dotenv()

stored_address = os.getenv('DATABASE_ADDRESS')
stored_password = os.getenv('DATABASE_PASSWORD')
stored_CGK_API_KEY = os.getenv('COINGEKCO_API_KEY')

api_receiver = api.Get_Api(stored_CGK_API_KEY)
inserting_data = api_receiver.get_top_10()
writer = DBR.Write_Data(stored_password,stored_address)
for item in inserting_data:
    writer.write_crypto_price(*item)
writer.connection_commit()
