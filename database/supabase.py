import psycopg2
from psycopg2 import extras
from models import BusinessListData , BusinessInsightData
import os 
from dotenv import load_dotenv

load_dotenv()

class Reader:
    def __init__(self):
        self.db_pool = psycopg2.pool.ThreadedConnectionPool(
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
     
    def write_business_list(self,data:BusinessListData):
        try:

            conn = None
            conn = self.db_pool.getconn()
            with conn.cursor() as cur:
                execute_values(cur , """
                INSERT INTO business_list (name,url,postal_code,country,street,locality,region,rating,review_count,telephone,opening_hours) 
                VALUES (%(name)s,%(url)s,%(postal_code)s,%(country)s,%(street)s,%(locality)s,%(region)s,%(rating)s,%(review_count)s,%(telephone)s,%(opening_hours)s)
                """, (data.model_dump()))

        except psycopg2.ProgrammingError as e:
            if conn:
                print(f"[ Write_Business_data | Data Error | ] : {e}")
                conn.rollback()
                return
        except psycopg2.OperationalError as e:
            if conn:
                print(f"[ Write_Business_data | Database's Operation Error | ] : {e}")
                conn.rollback()
                return 
        except psycopg2.IntegrityError as e:
            if conn:
                print(f"[ Write_Business_data | Database Intregrity Affected | ] : {e}")
                conn.rollback()
                return
        except psycopg2.Error as e:
            if conn:
                print(f"[ Write_Business_data ] : {e}")
                conn.rollback()
                return
        else:
            if conn:
                conn.commit()
        finally:
            if conn:
                conn.close()
