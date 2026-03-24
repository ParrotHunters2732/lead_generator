from database.supabase import Writer
from scraper.yellowpages import YellowPagesScraper

yellow_object = YellowPagesScraper("jewelry" , "NYC" , "NY")
data = yellow_object.get_business_list()
print(data)

