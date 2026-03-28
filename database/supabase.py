import psycopg2
from psycopg2 import extras , pool
from models import BusinessListData , BusinessInsightData
import os 
from dotenv import load_dotenv
import logging


load_dotenv()
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


class Reader:
    def __init__(self):
        self.db_pool = pool.ThreadedConnectionPool(
            1, 10, f"postgresql://postgres.{os.getenv('DATABASE_ADDRESS')}:{os.getenv('DATABASE_PASSWORD')}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
    
    def read(self):
        conn = None
        conn = self.db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("""
            SELECT * FROM crypto_prices
""")
            result = cur.fetchall()
            return result

    
class Writer(Reader):
    def write_crypto_price(self,symbol,name,price_usd,change_24h,market_cap):
        conn = None
        conn = self.db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO crypto_prices (symbol,name,price_usd,change_24h,market_cap) 
            VALUES (%s,%s,%s,%s,%s)
""", (symbol,name,price_usd,change_24h,market_cap,))
     
    def write_business_list(self,business_list_data: list):
        try:
            conn = None
            conn = self.db_pool.getconn()
            query = """
                INSERT INTO business_list (name,url,postal_code,country,street,rating,review_count,telephone,opening_hours,location_name,state_code) 
                VALUES %s
                """
            template="(%(name)s,%(url)s,%(postal_code)s,%(country)s,%(street)s,%(rating)s,%(review_count)s,%(telephone)s,%(opening_hours)s,%(location_name)s,%(state_code)s)"
            confirmed_data = [BusinessListData(**i) for i in business_list_data]
            data_dict = [i.model_dump() for i in confirmed_data]
            with conn.cursor() as cur:
                extras.execute_values(cur=cur , sql=query, argslist=data_dict, template=template)

        except psycopg2.ProgrammingError as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_list | 'supabase.py' | : {e}")
                raise SystemExit(1)
        except psycopg2.OperationalError as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_list | 'supabase.py' | : {e}")
                raise SystemExit(1)
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_list | 'supabase.py' | : {e}")
                raise SystemExit(1)
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_list | 'supabase.py' : {e}")
                raise SystemExit(1)
        else:
            if conn:
                conn.commit()
                logger.info("write_business_list | 'supabase' | Successfully wrote business list")
        finally:
                conn.close()

    def write_business_insight(self,dict_business_insight: dict):
        try:
            conn = None
            conn = self.db_pool.getconn()
            query = """
                INSERT INTO business_insight_data (name,category,description,adress,country,website,phone,email,payment,language,extralink,extra_phone) 
                VALUES (%(name)s,%(category)s,%(description)s,%(adress)s,%(country)s,%(website)s,%(phone)s,%(email)s,%(payment)s,%(language)s,%(extralink)s,%(extra_phone)s)
                """
            confirmed_data = BusinessInsightData(dict_business_insight)
            data_dict = confirmed_data.model_dump()
            print(data_dict)

            with conn.cursor() as cur:
                cur.execute(query,confirmed_data)

        except psycopg2.ProgrammingError as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_insight | 'supabase'| : {e}")
                raise SystemExit(1)
        except psycopg2.OperationalError as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_insight | 'supabase.py' | : {e}")
                raise SystemExit(1)
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_insight | 'supabase.py' | : {e}")
                raise SystemExit(1)
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                logger.critical(f"write_Business_insight | 'supabase.py' | : {e}")
                raise SystemExit(1)
        else:
            if conn:
                conn.commit()
                logger.info(" write_business_insight | supabase | Successfully wrote business list")
        finally:
                conn.close()