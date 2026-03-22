import requests

class Get_Api():
    base_url = "https://api.coingecko.com/api/v3/coins/markets"
    def __init__(self,key):
        self.api_key = key

    def get_top_10(self):
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1
        }
        headers = {
            "x-cg-demo-api-key": f"{self.api_key}" 
        }

        response = requests.get(Get_Api.base_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            parsed_data = [
                (item["symbol"], item["name"], item["current_price"], item["price_change_24h"], item["market_cap"])
                for item in data
            ]
            return parsed_data
        return response.status_code