import psycopg2
from psycopg2 import extras , pool
from models import BusinessListData , BusinessInsightData
import os 
from dotenv import load_dotenv
from logs.log import CustomLogger
from typing import Literal
from sqlparse import parse
from decorators import database_context_manager

logger = CustomLogger().get_logger(__name__)
load_dotenv()

class Reader:
    def __init__(self):
        self.db_pool = pool.ThreadedConnectionPool(
            1, 100, f"postgresql://postgres.{os.getenv('DATABASE_ADDRESS')}:{os.getenv('DATABASE_PASSWORD')}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
    
    @database_context_manager(mode="hidden")
    def get_url_and_unique_key(self, conn , limit_val: int):
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
    @database_context_manager(mode="hidden")
    def get_over_all(self,conn):
        with conn.cursor() as cur:
            cur.execute("""
            SELECT 
        (SELECT COUNT(*) FROM business_list) as total_business_list,
        (SELECT COUNT(*) FROM business_insight_data) as total_business_insight,
        (SELECT COUNT(*) FROM business_list 
         WHERE name IS NOT NULL AND url IS NOT NULL AND postal_code IS NOT NULL 
         AND street IS NOT NULL AND rating IS NOT NULL AND review_count IS NOT NULL 
         AND telephone IS NOT NULL AND opening_hours IS NOT NULL 
         AND location_name IS NOT NULL AND state_code IS NOT NULL) as perfect_leads,
        (SELECT COUNT(*) FROM business_list bl
         LEFT JOIN business_insight_data bid ON bl.unique_key = bid.unique_key 
         WHERE bid.unique_key IS NULL) as total_missing_bid,
        (SELECT COUNT (*) FROM business_insight_data
         WHERE name IS NOT NULL AND phone IS NOT NULL AND category IS NOT NULL 
         AND website IS NOT NULL AND email IS NOT NULL AND payment IS NOT NULL
         ) as legit_bid;""")
            result = cur.fetchall()
            if result:
                return result
            return {}
        
    @database_context_manager(mode="hidden")
    def get_business_rows(self,conn,setting:dict,table: Literal["business_list","business_insight_data"],limit: int=100):
        filter = [k for k,v in setting.items() if v]
        joined_filter = ",".join(filter)
        query = f"""SELECT {joined_filter} FROM {table} Limit {int(limit)};"""
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
            if result:
                return result
            return {}
        
    @database_context_manager(mode="hidden")
    def user_input_query(self,conn,user_query:str):
        parsed = parse(user_query)
        if len(parsed) != 1:
            raise psycopg2.IntegrityError("QUERY HAS LENGTH OVER THAN 1")
        statement = parsed[0]
        if statement.get_type() not in ("SELECT", "WITH"):
            raise psycopg2.IntegrityError("THERE ARE NO 'SELECT' / 'WITH' IN THE QUERY")
        forbidden_tokens = {"DELETE","DROP","TRUNCATE","UPDATE","INSERT","ALTER"}
        for token in statement.flatten():
            if token.is_keyword and token.value.upper() in forbidden_tokens:
                raise psycopg2.IntegrityError("DETECTED DESTRUCTIVE KEYWORD IN THE QUERY! **HIGHLY RECOMMEND DOING THIS OUTISDE THE SCRIPT")
        with conn.cursor() as cur:
            cur.execute(user_query)
            result = cur.fetchall()
            if result:
                return result
            return {}
        
    def close_all_connection(self):
        return self.db_pool.closeall()
    
class Writer(Reader):
    @database_context_manager(mode="display")
    def write_business_list(self,conn,business_list_data: list):
            query = """
                INSERT INTO business_list (name,url,postal_code,country,street,rating,review_count,telephone,opening_hours,location_name,state_code) 
                VALUES %s
                """
            template="(%(name)s,%(url)s,%(postal_code)s,%(country)s,%(street)s,%(rating)s,%(review_count)s,%(telephone)s,%(opening_hours)s,%(location_name)s,%(state_code)s)"
            confirmed_data = [BusinessListData(**i) for i in business_list_data]
            data_dict = [i.model_dump() for i in confirmed_data]
            with conn.cursor() as cur:
                extras.execute_values(cur=cur , sql=query, argslist=data_dict, template=template)

    @database_context_manager(mode="display")
    def write_business_insight(self,conn,dict_business_insight: dict,unique_key: str):
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

    