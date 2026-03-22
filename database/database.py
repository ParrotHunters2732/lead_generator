import psycopg2

class Read_Data:
    def __init__(self,password,address):
        self.address = address
        self.password = password
        self.connection = psycopg2.connect(f"postgresql://postgres.{self.address}:{self.password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
    def read(self):
        with self.connection.cursor() as cur:
            cur.execute("""
            SELECT * FROM crypto_prices
""")    
            result = cur.fetchall()
            return result
        
    def close_conn(self):
        if self.connection:
            self.connection.close()
            print("Connection_Closed")
        return


class Write_Data(Read_Data):
    def write_crypto_price(self,symbol,name,price_usd,change_24h,market_cap):
        with self.connection.cursor() as cur:
            cur.execute("""
            INSERT INTO crypto_prices (symbol,name,price_usd,change_24h,market_cap) 
            VALUES (%s,%s,%s,%s,%s)
""", (symbol,name,price_usd,change_24h,market_cap,))
            
    def connection_commit(self):
        if self.connection:
            self.connection.commit()
        return
            



    
        