from database.supabase import Writer
from scraper.yellowpages import YellowPagesScraper

yellow_object = YellowPagesScraper("plumber" , "NYC" , "NY")
data = yellow_object.get_business_list()[1]['url']
print(data)
insight = yellow_object.get_business_insight(target_url=data)
print(insight)

#Writer().write_business_insight(data)


