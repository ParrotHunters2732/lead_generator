import psycopg2


class ReadData:
    def __init__(self,password,address):
        self.address = address
        self.password = password
    
    def read(self):
        conn = None
        conn = psycopg2.connect(f"postgresql://postgres.{self.address}:{self.password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
        with conn.cursor() as cur:
            cur.execute("""
            SELECT * FROM crypto_prices
""")
            result = cur.fetchall()
            return result


class WriteData(ReadData):
    def write_crypto_price(self,symbol,name,price_usd,change_24h,market_cap):
        conn = None
        conn = psycopg2.connect(f"postgresql://postgres.{self.address}:{self.password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO crypto_prices (symbol,name,price_usd,change_24h,market_cap) 
            VALUES (%s,%s,%s,%s,%s)
""", (symbol,name,price_usd,change_24h,market_cap,))
