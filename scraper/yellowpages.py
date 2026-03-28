from bs4 import BeautifulSoup
import requests
import json
import time
import logging
from models import ConfigJson

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

with open('config.json', 'r') as f:
    try:
        confirmed_config_data = ConfigJson.model_validate_json(f.read()).model_dump()
    except Exception as e:
        logger.critical(f"The config is incompatible, change data in 'config.json': {e}")
        raise SystemExit(1)

class YellowPagesScraper:
    def __init__(self):
        self.headers = confirmed_config_data["headers"]

    def get_business_list(self,max_attempt: int , attempt_duration: float, category: str , location: tuple , page: int, session: str)->dict: 
        base_url = 'https://www.yellowpages.com/search?'
        params = {
            "search_terms": category,
            "geo_location_terms": location,
            "page": page,
            "s": "average_rating"
        }
        try:    
                session.headers.update(self.headers)
                response = session.get(url=base_url,params=params)
                content = response.content
                soup = BeautifulSoup(content,'html.parser')
                target_html_element = soup.find_all('script', type="application/ld+json")
                if not target_html_element:
                    for i in range(max_attempt):
                        retry_response = session.get(url=base_url,params=params)
                        retry_content = retry_response.content
                        retry_soup = BeautifulSoup(retry_content,'html.parser')
                        target_html_element = retry_soup.find_all('script', type="application/ld+json")
                        if not target_html_element:
                            logger.warning(f"get_business_list | 'yellowpages.py' | attemps : {i+1}")
                            logger.warning(f"get_business_list | 'yellowpages.py' | Response Status Code: {response.status_code}")
                            continue
                        elif target_html_element:
                            break

                if target_html_element:
                    for script in target_html_element:
                        if '"@type":"LocalBusiness"' in str(script):
                            stringtojson = json.loads(str(script.string))
                            final_clean_data = []
                            for item in stringtojson:
                                clean_data = {
                                    "name": item.get('name' , "N/A"),
                                    "url": item.get('url' , "N/A"),
                                    "postal_code": item.get('address' , {}).get('postalCode' , "N/A"),
                                    "country": item.get('address' , {}).get('addressCountry' , "N/A"),
                                    "street": item.get('address' , {}).get('streetAddress' , "N/A"),
                                    "rating": item.get('aggregateRating' , {}).get('ratingValue' , "N/A"),
                                    "review_count": item.get('aggregateRating' , {}).get('reviewCount' , "N/A"),
                                    "telephone": item.get('telephone' , "N/A"),
                                    "opening_hours": item.get('openingHours' , "N/A"),
                                    "location_name": item.get('address' , {}).get('addressLocality' , "N/A"),
                                    "state_code": item.get('address' , {}).get('addressRegion' , "N/A")
                                }
                                final_clean_data.append(clean_data)
                            return final_clean_data
                        
                return {}
        
        except requests.HTTPError as e:
            logger.error(f"get_business_list | 'yellowpages.py' | HTTP Error: {e}")
            return {}
        except requests.ConnectionError:
            logger.error("get_business_list | 'yellowpages.py' | Connection Failed")
            return {}
        except requests.Timeout:
            logger.error("get_business_list | 'yellowpages.py' | Timed Out")
            return {}
        except Exception as e:
            logger.error(f"get_business_list | 'yellowpages.py' | Failed: {e}")
            raise e

    def get_individual_object(self,soup_object,tag,attrs)->str:
        try:
            returning_data = soup_object.find(f'{tag}' , {"class": attrs})
            if returning_data:
                return returning_data
            return "N/A"
        except Exception as e:
            logger.error(f"get_individual_object | 'yellowpages.py '| Failed: {e}")
            return "N/A"
        

    def decode_cloudflare_email(self,cf_hex)->str:
        try:
            key = int(cf_hex[:2], 16)
            email = ""
            for i in range(2, len(cf_hex), 2):
                char_code = int(cf_hex[i:i+2], 16) ^ key
                email += chr(char_code)
            return email
        except (ValueError, IndexError) as e:
            logger.error(f"decode_cloudflare_email | 'yellowpages.py' | Failed: {e}")
            return "N/A"
    

    def get_business_insight(self,target_url: str)->dict:
        try:
            response = requests.get(target_url,headers=self.headers)
            soup = BeautifulSoup(response.text , 'html.parser')
    
            res_name = self.get_individual_object(soup, 'h1', 'dockable business-name')
            name = res_name.text if res_name != "N/A" else "N/A"

            res_cat = self.get_individual_object(soup, 'div', 'categories')
            category = "N/A" if res_cat == "N/A" else ", ".join([a.text for a in res_cat.find_all('a')])

            res_desc = self.get_individual_object(soup, 'dd', 'general-info')
            description = res_desc.text if res_desc != "N/A" else "N/A"
            
            res_addr = self.get_individual_object(soup, 'span', 'address')
            if res_addr != "N/A":
                street = res_addr.find('span')
                city_state = res_addr.find(string=True, recursive=False)
                address = f"{street.text}, {city_state.strip()}" if city_state else street
            else:
                address = "N/A"

            res_web = self.get_individual_object(soup, 'p', 'website')
            website = res_web.find('a')['href'] if (res_web != "N/A" and res_web.find('a')) else "N/A"

            phone = self.get_individual_object(soup, 'p', 'phone')
            if phone != "N/A":
                phone = phone.text.replace('Phone:', '').strip()
            else:
                phone = "N/A" 

            res_email = self.get_individual_object(soup, 'a', 'email-business')
            href = 'N/A' if res_email == 'N/A' else res_email.get('href', 'N/A')

            if href != 'N/A' and 'email-protection#' in href:
                cf_hex = href.split('#')[-1]
                key = int(cf_hex[:2], 16)
                email = "".join([chr(int(cf_hex[i:i+2], 16) ^ key) for i in range(2, len(cf_hex), 2)])
                href = email
            clean_email = href.replace('mailto:', '').split('?')[0].strip()
            
            payment = self.get_individual_object(soup, 'dd', 'payment')

            language = self.get_individual_object(soup, 'dd', 'languages')

            extra_links = self.get_individual_object(soup, 'dd', 'weblinks')

            extra_phone = self.get_individual_object(soup, 'dd', 'extra-phones') #return final extra phone list
            if extra_phone != "N/A":
                final_extra_phone = []
                for i in extra_phone:
                    spans = i.find_all('span')  
                    if len(spans) > 1:          
                            extra_individual_phone = spans[1]
                            final_extra_phone.append(extra_individual_phone.text)
            else:
                final_extra_phone = "N/A" 

            returning_data = {
                "name": name,
                "category": category,
                "description": description,
                "address": address,
                "website": website,
                "phone": phone,
                "email": clean_email,
                "payment": payment.text if payment != "N/A" else "N/A",
                "language": language.text if language != "N/A" else "N/A",
                "extra_links": extra_links.text if extra_links != "N/A" else "N/A",
                "extra_phone": final_extra_phone
            }
            return returning_data
        
        except requests.HTTPError as e:
            logger.error(f"get_business_list | 'yellowpages.py' | HTTP Error: {e}")
            return {}
        except requests.ConnectionError:
            logger.error("get_business_list | 'yellowpages.py' | Connection Failed")
            return {}
        except requests.Timeout:
            logger.error("get_business_list | 'yellowpages.py' | Timed Out")
            return {}
        except Exception as e:
            logger.error(f"get_business_list | 'yellowpages.py' | Failed: {e}")
            return {}

