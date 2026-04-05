import psycopg2
from psycopg2 import extras , pool
from models import BusinessListData , BusinessInsightData
import os 
from dotenv import load_dotenv
from logs.log import CustomLogger


logger = CustomLogger().get_logger(__name__)
load_dotenv()

class Reader:
    def __init__(self):
        self.db_pool = pool.ThreadedConnectionPool(
            1, 100, f"postgresql://postgres.{os.getenv('DATABASE_ADDRESS')}:{os.getenv('DATABASE_PASSWORD')}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
    

    def get_url_and_unique_key(self, limit_val: int):
        try:
            conn = None
            conn = self.db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute("""
                SELECT bl.url , bl.unique_key
                FROM business_list bl
                LEFT JOIN business_insight_data bid ON bl.unique_key = bid.unique_key
                WHERE bid.unique_key IS NULL
                LIMIT %(limit)s;
    """,{"limit": limit_val})
                result = cur.fetchall()
                if result:
                    return result
                return {}
            
        except psycopg2.ProgrammingError as e:
            if conn:
                conn.rollback()
                logger.critical(f"get_url_and_unique_key | 'supabase'| : {e}")
                raise SystemExit(1)
        except psycopg2.OperationalError as e:
            if conn:
                conn.rollback()
                logger.critical(f"get_url_and_unique_key | 'supabase.py' | : {e}")
                raise SystemExit(1)
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
                logger.critical(f"get_url_and_unique_key | 'supabase.py' | : {e}")
                raise SystemExit(1)
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                logger.critical(f"get_url_and_unique_key | 'supabase.py' | : {e}")
                raise SystemExit(1)
        else:
            if conn:
                conn.commit()
        finally:
            if conn:
                self.db_pool.putconn(conn)

    
class Writer(Reader):
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
                logger.info("write_business_list | 'supabase.py' | Successfully wrote business list")
        finally:
            if conn:
                self.db_pool.putconn(conn)

    def write_business_insight(self,dict_business_insight: dict,unique_key: str):
        try:
            conn = None
            conn = self.db_pool.getconn()
            confirmed_data = BusinessInsightData(**dict_business_insight)
            data_dict = confirmed_data.model_dump()
            data_dict["unique_key"] = unique_key
            query = """
                INSERT INTO business_insight_data (
                    name, category, description, address, website, 
                    phone, email, payment, language, extra_links, 
                    extra_phone, unique_key
                )
                VALUES (
                    %(name)s, %(category)s, %(description)s, %(address)s, %(website)s, 
                    %(phone)s, %(email)s, %(payment)s, %(language)s, %(extra_links)s, 
                    %(extra_phone)s, %(unique_key)s
                )
            """
            with conn.cursor() as cur:
                cur.execute(query,data_dict)
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
                logger.info("write_business_insight | 'supabase.py' | Successfully wrote business list")
        finally:
            if conn:
                self.db_pool.putconn(conn)

    def close_all_connection(self,conn):
        return self.db_pool.closeall()