import streamlit as st
from helpers import get_json_config_dict, write_new_config, pop_ups, database_popups, is_there_database_info, percentage, get_newest_logs,basic_exception_handling
from logs.log import CustomLogger
from utils import GetAndStoreData
from database.supabase import Reader
import pandas as pd

logger = CustomLogger().get_logger(__name__)

class App:
    @basic_exception_handling
    def __init__(self):
        confirmed_config_data = {}
        confirmed_config_data = get_json_config_dict()
        if not is_there_database_info(mode="status"): #doesnt have database info
            st.markdown("Enter Project info before use!!")
            if st.button("Enter info"):
                database_popups()
        if not confirmed_config_data:
            logger.critical("'Config.json'doesnt have data")
            st.stop()

        elif confirmed_config_data:
            self.all_config = confirmed_config_data
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
            self.db_reader = Reader()
    
    @basic_exception_handling
    def home_page(self):
        st.title("🏠 | Home")
        st.divider()
        st.header("🔥 | Quick Start Navigation Guide")
        st.markdown("""
                \nWelcome! Use this guide to quickly find the tools you need to extract, analyze, and manage your business data.
                \n**Targeted Extraction**: It scrapes high-level business lists and deep-dive insights based on your specific configurations.
                \n**Database Management**: It stores your results in a central hub where you can view overall stats or run custom SQL queries for advanced analysis.
                \n**Custom Reporting**: It allows you to filter specific data points and export them into clean CSV files for your sales or marketing teams.
                \n**System Transparency**: It provides real-time logs and a detailed help manual to ensure your extractions run smoothly and safely.
                \n---""")
        st.header("🏠 | Home Page")
        st.markdown("""
                \n**Purpose**: Get oriented with this quick-start guide. Use this page to understand how to move between extraction and data management.
                \n**Onboarding**: Contains the "Quick Navigation Guide" to ensure users don't get lost between extraction and data management.
                \n---""")
        st.header("💻 | Scraper")
        st.subheader("**Extract Business List (The Quick Scan)**")
        st.markdown("""
                \n**Identity & Reputation**: Extract the Business Name, Rating, and Review Count to help you prioritize high-quality leads.
                \n**Geographic Data**: Automatically pulls the Country, State Code, Postal Code, Street Address, and Location Name.
                \n**Operational Details**: Collects the direct Inner yellowpages_URL, Telephone number, and Opening Hours.
                \n**Traceability**: Every entry is marked with a Timestamp so you know exactly when the lead was discovered.
                \n---""")
        st.subheader("**Extract Business Insights (The Deep Dive)**")
        st.markdown("""
                \n**Contact Expansion**: Beyond basic info, you can extract Emails, Extra Phone Numbers, and Extra Links (social media or secondary sites).
                \n**Business Profile**: Pull the full Description, Category classifications, and supported Languages.
                \n**Commercial Data**: Pull Payment Methods accepted by the business and Pull the official Website and Physical Address.
                \n---""")
        st.subheader("**View Config (The System Monitor)**")
        st.markdown("""
                \nTo ensure accuracy, this tab displays a Live Snapshot of your current scraper settings.
                \n**Verification**: Check your current Configuration, location, or category settings before starting a run.
                \n**Read-Only Security**: This tab is locked for editing to prevent accidental changes while a process is running; all adjustments must be made in the Configuration page.
                \n---""")    
        st.header("📝 | Log Page")
        st.markdown("""
                \nThis page is for transparency and troubleshooting.
                \n**Activity Tracking**: Every action the scraper takes is timestamped. If an extraction stops midway, the logs will tell you if it was a connection error, a rate limit, or a finished task.
                \n**Audit Trail**: Essential for technical support to see exactly what happened during a session.
                \n---""")
        st.header("ℹ️ | Help Page")
        st.markdown("""
                \nThe comprehensive manual designed to make users self-sufficient.
                \n**Standard Operating Procedures (SOPs)**: Detailed guides on how to set up your first configuration correctly.
                \n**Error Documentation**: A "Dictionary of Errors" that explains what specific log messages mean and how to fix them.
                \n**The Help Page**: serves as a comprehensive manual for the suite, covering everything from initial setup (Supabase integration and header authentication) to operational logic like rate limiting and error recovery. It establishes critical rules for IP safety and database integrity while providing a legal framework regarding user responsibility and compliance. Essentially, it is designed to turn new users into self-sufficient operators who can safely extract, manage, and query data without technical friction.
                \n---""")
    @basic_exception_handling
    def scraper_page(self):
        with st.container():
            st.title("💻 | Scrape Bussines Data")
            st.divider()
            Business_List , Business_Insight , Configuration = st.tabs(["📝 | Business List","📊 | Business Insight","⚙️ | Configuration"])

            with Business_List:
                col1bl , col2bl , col3bl = st.columns(3)
                col2bl_placehold = col2bl.empty()
                if col1bl.button("Start Scraping!",key="business_list_button1"):
                    if col2bl_placehold.button("quit",help="Quitting during scraping can result in duplicate data "):
                        st.stop()
                    init = st.progress(text="Initializing..",value=100)
                    placehold = st.empty()
                    for index , result in GetAndStoreData().business_list(category=self.category,location=self.location):
                        init.progress(text="Scraping..",value=percentage(value=index,total=self.page_per_request))
                        if result:
                            placehold.success(f"Successfully Scrape page : {index}/{self.page_per_request}",width="stretch")
                        else:
                            placehold.error(f"Failed on page : {index}",width="stretch")
                    init.progress(text="Finished.",value=100)
                    col2bl_placehold.write("")
        
            with Business_Insight:
                col1bi , col2bi , col3bi = st.columns(3)
                col2bi_placehold = col2bi.empty()
                if col1bi.button("Start Scraping!",width="content",key="business_insight_button1"):
                    if col2bi_placehold.button("quit"):
                        st.stop()
                    init = st.progress(text="Initializing..",value=100)
                    length_url_and_unique_key = len(self.db_reader.get_url_and_unique_key(self.amount_write_business_insight))
                    placehold = st.empty()
                    for index , result in GetAndStoreData().business_insight():
                        init.progress(text="Scraping..",value=percentage(value=index+1,total=length_url_and_unique_key))
                        if result:
                            placehold.success(f"Successfully Scrape page : {index+1}/{length_url_and_unique_key}",width="stretch")
                        else:   
                            placehold.error(f"Failed on page : {index}",width="stretch")
                    init.progress(text="Finished.",value=100)
                    col2bi_placehold.empty()

            with Configuration:
                    st.json(self.all_config)

    @basic_exception_handling
    def config(self):
        st.title("⚙️ | Configuration")
        with st.popover(label="Current Configuration",width="content"):
            self.all_config
        with st.form(key="form",enter_to_submit=False):
            page_per_request = st.number_input(label="Page Per Requests (Amount)",min_value=1,max_value=100,value=self.page_per_request)
            rate_min = st.number_input(label="Rate Minimum (Second/s)",min_value=0.1,max_value=10.0,value=self.rate_min,step=0.25)
            rate_max = st.number_input(label="Rate Maximum (Second/s)" ,min_value=0.1,max_value=10.0,value=self.rate_max,step=0.25)
            max_attempt = st.number_input(label="Max Attempt (Amount)",min_value=0,max_value=10,value=self.max_attempt)
            attempt_duration = st.number_input(label="Attempt's Duration (Second/s)",min_value=1.0,max_value=100.0,value=self.attempt_duration,step=0.25)
            redo_on_fail_page = st.toggle(label="Redo on fail page (On/Off)",value=self.redo_on_fail_page)
            redo_on_fail_page_attempt = st.number_input(label="redo on fail page Attempt (Amount)",min_value=0,max_value=10,value=self.redo_on_fail_page_attempt)


            category = st.text_input(label="category",max_chars=None,value=self.category)
            location = st.text_input(label="location",max_chars=None,value=self.location)
            
            cookies_mention = "(**highly recommend to add cookies | cookies currently **DOESNT exist!)" if self.cookies == "" else ""
            cookies = st.text_input(label=f"cookies {cookies_mention}",max_chars=None,placeholder="Insert new Cookies here!!")

            amount_write_business_insight = st.number_input(label="Amount to write business insight (Amount)",min_value=1,max_value=5000,value=self.amount_write_business_insight)
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
                addr_hidden_pass=pd.DataFrame(data=(db_address,db_password_hidden),columns=["Project's info"],index=["Project's ID","Password"])
                addr_hidden_pass
                if st.button("change project's info"):
                    database_popups()
        st.divider()


    @basic_exception_handling
    def data_page(self):
        st.title("📊 | Data")
        st.divider()
        overall_tab , data_selector , custom_query = st.tabs(["Overall","Data Selector","Custom Query"])
        with overall_tab:
            st.space("small")
            placehold = st.empty()
            placehold.progress(value=100,text="Loading..")
            total_business_list,total_business_insight,perfect_leads,total_missing_bid,legit_bid = self.db_reader.get_over_all()[0]
            missing_percentage = (total_missing_bid / total_business_list) * 100 if total_business_list != 0 else 0
            filled_percentage = 100-missing_percentage if total_business_list != 0 and total_business_insight != 0 else 0
            col1 , col2 = placehold.columns(2)
            with col1:
                col1.subheader("Total Business List :")
                col1.subheader("Total Business Insight :")
                col1.subheader("Missing Business Insight :")
                col1.subheader("Missing percentage:")
                col1.subheader("Filled percentage :")
                col1.subheader("Perfect lead :")
                col1.subheader("legit insight data:")
            with col2: 
                col2.subheader(body=(f'{total_business_list:,}'))
                col2.subheader(body=(f'{total_business_insight:,}'))
                col2.subheader(body=(f'{total_missing_bid:,}'))
                col2.subheader(body=(f'{missing_percentage:.2f} %'))
                col2.subheader(body=(f'{filled_percentage:.2f} %'))
                col2.subheader(body=(f'{perfect_leads:,}'))
                col2.subheader(body=(f'{legit_bid:,}'))
        with data_selector:
            option = st.selectbox(label="Select one [Business List / Business insight]",options=("Business list","Business insight"))
            col1ds , col2ds , col3ds , col4ds , col5ds , col6ds = st.columns(6)
            if option == "Business list":
                with col1ds.popover(label="Filter"):
                    with st.form(key="options_form"):
                        name = st.checkbox(label="name")
                        url = st.checkbox(label="url")
                        postal_code = st.checkbox(label="postal code")
                        country = st.checkbox(label="country")
                        location = st.checkbox(label="location")
                        street = st.checkbox(label="street")
                        state_code = st.checkbox(label="State code")
                        rating = st.checkbox(label="rating")
                        review_count = st.checkbox(label="review count")
                        telephone = st.checkbox(label="telephone")
                        opening_hours = st.checkbox(label="opening hours")
                        Timestamp = st.checkbox(label="Timestamp")

                        limit = st.number_input(label="limit",step=25,value=100)
                        st.form_submit_button(label="apply")
                        options = {
                            "name": name,
                            "url" : url,
                            "postal_code": postal_code,
                            "country": country,
                            "location_name" : location,
                            "street": street,
                            "state_code": state_code,
                            "rating":rating,
                            "review_count": review_count,
                            "telephone":telephone,
                            "opening_hours": opening_hours,
                            "timestamp": Timestamp
                    }
                    table = "business_list"

            elif option == "Business insight":
                with col1ds.popover(label="Filter"):
                    with st.form(key="options_form_bi"):
                        name_bi = st.checkbox(label="name")
                        phone_bi = st.checkbox(label="phone")
                        category_bi = st.checkbox(label="category")
                        description_bi = st.checkbox(label="description")
                        address_bi = st.checkbox(label="address")
                        website_bi = st.checkbox(label="website")
                        email_bi = st.checkbox(label="email")
                        payment_bi = st.checkbox(label="payment")
                        language_bi = st.checkbox(label="language")
                        extra_links_bi = st.checkbox(label="extra links")
                        extra_phone_bi = st.checkbox(label="extra phone")
                        timestamp_bi = st.checkbox(label="timestamp")
                        limit = st.number_input(label="limit",step=25,value=100)
                        st.form_submit_button(label="apply")
                        options = {
                            "name": name_bi,
                            "phone" : phone_bi,
                            "category": category_bi,
                            "description": description_bi,
                            "address" : address_bi,
                            "website": website_bi,
                            "email": email_bi,
                            "payment": payment_bi,
                            "language": language_bi,
                            "extra_links":extra_links_bi,
                            "extra_phone": extra_phone_bi,
                            "timestamp": timestamp_bi,
                        }
                        table = "business_insight_data"
            if col2ds.button(label="Pull Data"):
                placehold = st.empty()
                placehold.progress(value=100,text="Loading..")
                result = self.db_reader.get_business_rows(setting=options,table=table,limit=int(limit))
                placehold.write('')
                if result:
                    total = [k for k,v in options.items() if v]
                    df = pd.DataFrame(data=result,columns=total)
                    df.index = df.index + 1
                    df
                else:
                    st.markdown("0 rows returns")
        with custom_query:
            user_query = st.text_area(label="",placeholder="Paste your queries here!!",label_visibility="hidden")
            st.write("NOTE THAT 'TRUNCATE' | 'DELETE' | 'DROP' QUERY ARE NOT ALLOW!")
            col1cq,col2cq,col3cq,col4cq,col5cq ,col6cq, = st.columns(6)
            if col6cq.button(label="Execute"):
                resultcq = self.db_reader.user_input_query(user_query=user_query)
                if resultcq:
                    df = pd.DataFrame(data=resultcq)
                    df.index = df.index + 1 
                    df
                else:
                    st.write("Return 0 row.")
    @basic_exception_handling
    def log_page(self):
        st.title("📝 | Logs")
        st.divider()
        placehold3 = st.empty()
        placehold3.progress(value=100,text="Loading..")
        amount = placehold3.selectbox(label="Amount line to display!",options=[100,300,500,1000])
        if amount:
            st.divider()
            result = get_newest_logs(n=amount)
            for line in result:
                st.write(line)
        
    @basic_exception_handling
    def help(self):
        st.title("ℹ️ | Guide")
        st.divider()
        st.header("🔨 | Set-up")
        st.subheader("Database Integration")
        st.markdown("""
        \n Step 1: Create a new project at Supabase.
        \nStep 2: Note down your Project ID and Database Password.
        \nStep 3: Navigate to the bottom of the Config Page in this app and enter these credentials to link your database. (in this script can be change anytime)
        \nStep 4: copy and paste this table setup in **Table Editor** follow in order
        """) 
        st.code("""
            create table public.business_list (
            name text null,
            url text null,
            postal_code text null,
            country text null,
            street text null,
            location_name text null,
            state_code text null,
            rating numeric(2, 1) null,
            review_count integer null,
            telephone text null,
            opening_hours text null,
            unique_key uuid not null default gen_random_uuid (),
            timestamp timestamp with time zone null default (now() AT TIME ZONE 'utc'::text),
            constraint business_list_pkey primary key (unique_key)
            ) TABLESPACE pg_default;
            """)
        st.code("""
            create table public.business_insight_data (
            name text null,
            category text null,
            description text null,
            address text null,
            website text null,
            phone character varying(30) null,
            email text null,
            payment text null,
            language text null,
            extra_links text null,
            extra_phone text null,
            unique_key uuid not null,
            timestamp timestamp with time zone null default (now() AT TIME ZONE 'utc'::text),
            constraint business_insight_data_pkey primary key (unique_key),
            constraint business_insight_data_unique_key_fkey foreign KEY (unique_key) references business_list (unique_key) on delete CASCADE
            ) TABLESPACE pg_default;
        \n""")
        st.divider()
        st.subheader("Initial Header Setup")
        st.markdown("""
        \nStep 1: Open YellowPages.com and right-click to Inspect > Network tab.
        \nStep 2: Refresh the page and select the first request with a 200 Status Code.
        \nStep 3: Copy the data from the Request Headers section.
        \nStep 4: Open your main file and locate Line (163.). Ensure the field "cookie_string": "" is present and empty. if not insert at any part of your header
        \nStep 5: Save your configuration once to initialize the session.
        \n---""")
        st.subheader("Browser Authentication (Recommended)")
        st.markdown("""
        \nStep 3.1: For better stability, download the Cookie Editor browser extension.
        \nStep 3.2: Go to the YellowPages website and open the extension.
        \nStep 3.3: Select Export as Header String to copy your active session data.
        \nStep 3.4: Paste this into your configuration and click Save. 
        \n---""")
        st.subheader("Final Check")
        st.markdown("""
        Once your database is linked and your headers are updated, you are ready to start your first scrape from the Scrape Page.\n
""")
        st.divider()
        st.header("⚙️ | Configuration Guide")
        st.space('small')
        st.subheader("Core Scrape Logic")
        st.markdown("""
        \n**Page per Request (PPR)**: Defines the total number of business list pages to scrape in a single session.
        \n**Rate Min / Max**: Sets a random delay (float) between page requests to mimic human browsing behavior.
        \n**Max Attempt**: The retry limit per page. If Page 3 fails, the system will immediately retry it up to this amount before moving on.
        \n**Attempt Duration**: The maximum time in seconds the system waits for a response during a retry attempt.
        \n---""")
        st.subheader("Error Recovery & Session Cleanup")
        st.markdown("""
        \n**Redo on Fail Page**: When enabled, the system compiles a list of all pages that failed during the initial run and retries them after the session ends.
        \n**Redo Attempt**: Specifies how many times the system should try to recover those specific failed pages during the cleanup phase.
        \n---""")
        st.subheader("Targeting & Scope")
        st.markdown("""
        \n**Category**: The business niche or industry keyword (e.g., jewelry).\n
        \n**Location**: The geographic area targeted for the search (e.g., NYC, NY).\n
        \n**Amount of Page Insight**: The total number of businesses to deep-scan for detailed contact and profile information.\n 
        \n---""")
        st.subheader("Network Identity")
        st.markdown("""
        \n**Header**: The technical fingerprint (User-Agent and Cookies) used to verify the connection and maintain a stable session with the source.\n
        \n---""")
        st.header("📜 | Rules Of Thumbs")
        st.subheader("Critical System Rules")
        st.markdown("""
        **Single Session**: Only run one scrape instance at a time to prevent data conflicts.
        \n**Config Locking**: Settings are read-only during active processes; finalize your config before starting.
        \n**Database Guardrails**: While railguards exist for destructive commands, use the **Custom Query** tab for reading and extracting only.
        \n---
        """)
        st.subheader("Scraping Etiquette & IP Safety")
        st.markdown("""
        **Avoid Redundancy**: Rerunning the same category/location causes high duplicate rates. Scrape once for the max amount (~100 pages/3000 businesses) for efficiency.
        \n**IP Protection**: Aggressive scraping in short bursts increases ban risk. Use realistic delays.
        \n**Cookie Maintenance**: Refresh your cookie string if failure rates spike to maintain a "human" profile.
        \n---
        """)
        st.subheader("Professional Tips")
        st.markdown("""
        **Custom Data Retrieval**: Use the **Custom Query** tab to isolate high-value leads on your own terms before exporting.
        \n**Advanced Manipulation**: For table structural changes, we highly encourage using the **Supabase Dashboard** directly.
        \n---
        """)
        st.header("⚖️ Legal & Compliance")
        st.subheader("**End User License & Disclaimer**")
        st.markdown("""
        **Use at Your Own Risk**: This software is provided "**as is**" without warranty of any kind. The developer is not responsible for any IP bans, legal disputes, or data loss incurred through the use of this tool.
        \n  **Compliance Responsibility**: Users are solely responsible for ensuring their scraping activities comply with the target website's Terms of Service and local privacy laws (such as GDPR or CCPA).
        \n**Internal Use Only**: This tool is designed for internal lead generation. Unauthorized redistribution of this software or the commercial resale of scraped data without proper authorization is strictly prohibited.
        \n---
        """)

app_maker = App()
pages = [
    st.Page(page=app_maker.home_page,title="Home",icon="🏠",url_path="home",default=True),
    st.Page(page=app_maker.scraper_page,title="Scrape",icon="💻",url_path="scraper",default=False),
    st.Page(page=app_maker.data_page,title="Data",icon="📊",url_path="data",default=False),
    st.Page(page=app_maker.config,title="Configuration",icon="⚙️",url_path="config",default=False),
    st.Page(page=app_maker.log_page,title="Logs",icon="📝",url_path="log_page",default=False),
    st.Page(page=app_maker.help,title="Help",icon="ℹ️",url_path="help",default=False)
]
nav = st.navigation(pages)
nav.run()
