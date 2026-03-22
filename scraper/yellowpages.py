from bs4 import BeautifulSoup
import requests
import json


class YellowPagesScraper:

    def __init__(self,category: str , borough: str , city: str):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding" : "gzip, deflate, br, zstd",
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
            "Accept-Language" : "en-US,en;q=0.9",
            "Referer" : f"https://www.yellowpages.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin"
        }
        self.url_search_path = f"https://www.yellowpages.com/search?search_terms={category}&geo_location_terms={borough}%2C+{city}&s=average_rating"


    def get_business_list(self)->dict: 
        try:
            response = (requests.get(self.url_search_path,headers=self.headers)).content
            soup = BeautifulSoup(response,'html.parser')
            target_html_element = soup.find_all('script', type="application/ld+json")
            stringtojson = json.loads(str(target_html_element[1].string))
            final_clean_data = []
            for item in stringtojson:
                clean_data = {
                    "name": item.get('name' , "N/A"),
                    "url": item.get('url' , "N/A"),
                    "postal_code": item.get('address' , {}).get('postalCode' , "N/A"),
                    "country": item.get('address' , {}).get('addressCountry' , "N/A"),
                    "street": item.get('address' , {}).get('streetAddress' , "N/A"),
                    "locality": item.get('address' , {}).get('addressLocality' , "N/A"),
                    "region": item.get('address' , {}).get('addressRegion' , "N/A"),
                    "rating": item.get('aggregateRating' , {}).get('ratingValue' , "N/A"),
                    "review_count": item.get('aggregateRating' , {}).get('reviewCount' , "N/A"),
                    "telephone": item.get('telephone' , "N/A"),
                    "opening_hours": item.get('openingHours' , "N/A"),
                }
                final_clean_data.append(clean_data)
            return final_clean_data
        except requests.HTTPError as e:
            print(f"[Business_list] HTTP Error: {e}")
            return {}
        except requests.ConnectionError:
            print("[Business_list] Connection Failed")
            return {}
        except requests.Timeout:
            print("[Business_list] Timed Out")
            return {}
        except Exception as e:
            print(f"[Business_list] Failed: {e}")
            return {}
        

    def get_url(self)->str:
        return self.url_search_path


    def get_individual_object(self,soup_object,tag,attrs)->str:
        try:
            returning_data = soup_object.find(f'{tag}' , {"class": attrs})
            if returning_data:
                return returning_data
            return "N/A"
        except Exception as e:
            print(f"[get_business_insight] Failed: {e}")
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
            print(f"[decode_cloudflare_email] Failed: {e}")
            return "N/A"


    def get_business_insight(self,target_url)->dict:
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
            street = res_addr.find('span').text if res_addr.find('span') else "N/A"
            city_state = res_addr.find(string=True, recursive=False)
            address = f"{street}, {city_state.strip()}" if city_state else street

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
            print(f"[get_business_insight] HTTP Error: {e}")
            return {}
        except requests.ConnectionError:
            print("[get_business_insight] Connection Failed")
            return {}
        except requests.Timeout:
            print("[get_business_insight] Timed Out")
            return {}
        except Exception as e:
            print(f"[get_business_insight] Failed: {e}")
            return {}

