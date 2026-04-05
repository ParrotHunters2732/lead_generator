import streamlit as st
from helpers import get_json_config_dict , write_new_config , pop_ups ,database_popups , is_there_database_info
from logs.log import CustomLogger
import pandas as pd

logger = CustomLogger().get_logger(__name__)

class App:
    def __init__(self):
        confirmed_config_data = {}
        confirmed_config_data = get_json_config_dict()
        if confirmed_config_data:
            self.page_per_request = confirmed_config_data.get("page_per_request",None)
            self.rate_min = confirmed_config_data.get("rate_min",None)
            self.rate_max = confirmed_config_data.get("rate_max",None)
            self.max_attempt = confirmed_config_data.get("max_attempt",None)
            self.attempt_duration = confirmed_config_data.get("attempt_duration",None)
            self.write_business_insight_on_loop = confirmed_config_data.get("write_business_insight_on_loop",None)
            self.write_business_insight_loop_cooldown = confirmed_config_data.get("write_business_insight_loop_cooldown",None)
            self.redo_on_fail_page = confirmed_config_data.get("redo_on_fail_page",None)
            self.redo_on_fail_page_attempt = confirmed_config_data.get("redo_on_fail_page_attempt",None)
            self.category = confirmed_config_data.get("category",None)
            self.location = confirmed_config_data.get("location",None)
            self.header = confirmed_config_data.get("header",None)
            self.cookies = confirmed_config_data.get("header",{}).get("cookies_string")
            self.amount_write_business_insight = confirmed_config_data.get("amount_write_business_insight",None)
        else:
            logger.critical("'Config.json'doesnt have data")
            SystemExit(1)

    def home_page(self):
        st.title("Home")
        st.header("MY HOME!")
        st.text("this is my home and i live here")
    def scraper_page(self):
        st.title("Scrape Busines Data")
        st.header("Scrape Interface!")
        if st.button("Scrape_data"):
            print("scraping_data")
        if st.button("Stop_scrape"):
            print("stop!")
        st.text("here is things about us")

    def config(self):
        st.title("⚙️ | Configuration")
        with st.form(key="form"):
            page_per_request = st.number_input(label="Page Per Requests (Amount)",min_value=1,max_value=100,value=self.page_per_request)
            rate_min = st.number_input(label="Rate Minimum (Second/s)",min_value=0.1,max_value=10.0,value=self.rate_min,step=0.25)
            rate_max = st.number_input(label="Rate Maximum (Second/s)" ,min_value=0.1,max_value=10.0,value=self.rate_max,step=0.25)
            max_attempt = st.number_input(label="Max Attempt (Amount)",min_value=0,max_value=10,value=self.max_attempt)
            attempt_duration = st.number_input(label="Attempt's Duration (Second/s)",min_value=1.0,max_value=100.0,value=self.attempt_duration)
            redo_on_fail_page = st.toggle(label="Redo on fail page (On/Off)",value=self.redo_on_fail_page)
            redo_on_fail_page_attempt = st.number_input(label="redo on fail page Attempt (Amount)",min_value=0,max_value=10,value=self.redo_on_fail_page_attempt)


            category = st.text_input(label="category",max_chars=None,value=self.category)
            location = st.text_input(label="location",max_chars=None,value=self.location)
            
            cookies_mention = "(**highly recommend to add cookies | cookies currently **DOESNT exist!)" if self.cookies == "" else ""
            cookies = st.text_input(label=f"cookies {cookies_mention}",max_chars=None,placeholder="Insert new Cookies here!!")

            amount_write_business_insight = st.number_input(label="Amount to write business insight (Amount)",min_value=1,max_value=1000,value=self.amount_write_business_insight)
            submited = st.form_submit_button(label="Save")            
            if submited:
                write_new_config(
                    {
                    "page_per_request": int(page_per_request),
                    "rate_min" : float(rate_min),
                    "rate_max" : float(rate_max) ,
                    "max_attempt": int(max_attempt),
                    "attempt_duration" : float(attempt_duration),
                    "redo_on_fail_page": bool(redo_on_fail_page),
                    "redo_on_fail_page_attempt": int(redo_on_fail_page_attempt),
                    "category": str(category),
                    "location": str(location),
                    "header" :  { "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
                                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                                    "Accept-Language": "en-US,en;q=0.5",
                                    "Accept-Encoding": "gzip, deflate, br",
                                    "Referer": "https://www.yellowpages.com/",
                                    "DNT": "1",
                                    "Connection": "keep-alive",
                                    "Upgrade-Insecure-Requests": "1",
                                    "Sec-Fetch-Dest": "document",
                                    "Sec-Fetch-Mode": "navigate",
                                    "Sec-Fetch-Site": "same-origin",
                                    "Sec-Fetch-User": "?1",
                                    "cookies_string": str(self.cookies if cookies == "" else cookies)
                                },
                    "amount_write_business_insight": int(amount_write_business_insight)
                    }
                )
                with st.empty():
                    pop_ups("Saved changes!") if submited else ""
                    st.write("")
                    st.rerun()
        st.divider(width="stretch")
        st.header("💾 | Database Configuration")
        if not is_there_database_info(mode="status"): #doesnt have database info
            st.markdown("Seems like you haven't enter Supabase project's info!")
            if st.button("Enter info"):
                database_popups()
        else: #has database info
                db_address,db_password_hidden = is_there_database_info(mode="hidden")
                st.dataframe(data=(db_address,db_password_hidden))
                if st.button("change project's info"):
                    database_popups()
                    

                
            


    def data_page(self):
        st.title("data")
        st.header("Display data!")
        st.text("here is things about us")
    def help(self):
        st.title("Guide")
        st.header("Quick Guide!")

app_maker = App()
pages = [
    st.Page(page=app_maker.home_page,title="Home",icon="🏠",url_path="home",default=True),
    st.Page(page=app_maker.scraper_page,title="Scrape",icon="💻",url_path="scraper",default=False),
    st.Page(page=app_maker.data_page,title="Data",icon="📊",url_path="data",default=False),
    st.Page(page=app_maker.config,title="Configuration",icon="⚙️",url_path="config",default=False),
    st.Page(page=app_maker.help,title="Help",icon="ℹ️",url_path="help",default=False)
]
nav = st.navigation(pages)
nav.run()
