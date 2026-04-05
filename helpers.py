from models import ConfigJson
from decorators import basic_exception_handling
from json import dump
import streamlit as st
from time import sleep
import os
from dotenv import load_dotenv
from typing import Literal

@basic_exception_handling
def get_json_config_dict()-> dict:
    with open('config.json', 'r') as f:
        confirmed_config_data_dict = ConfigJson.model_validate_json(f.read()).model_dump()
        return confirmed_config_data_dict

@basic_exception_handling
def write_new_config(user_submit: dict)->None:
    with open('config.json' ,'w') as f:
        validated_data = ConfigJson.model_validate(user_submit).model_dump()
        dump(validated_data,f,indent="\t")

@basic_exception_handling
def is_there_database_info(mode: Literal["status","hidden"])-> bool | str:
    if not load_dotenv(override=True):
        return False
    
    db_address = os.getenv("DATABASE_ADDRESS")
    db_password = os.getenv("DATABASE_PASSWORD")

    if mode == "status":
        return db_address is not None and db_password is not None
    elif mode == "hidden":
        return db_address , (len(db_password) * "*")
    else:
        raise ValueError("| is_there_database_info | only takes two type of argument which are 'status' / 'hidden'")

def write_db_info_dotenv(address:str , password:str)->None:
    with open('.env','w') as f:
        f.write(f'DATABASE_ADDRESS="{address}"\n')
        f.write(f'DATABASE_PASSWORD="{password}"')

# ------- Streamlit Object -------

def pop_ups(text)->None:
    with st.empty():
        st.write(f":material/check: {text}")
        sleep(1.75)

@st.dialog("🔑 | Supabase Authentication",width="medium",on_dismiss='rerun')        
def database_popups():
    if "database_address" not in st.session_state:
        st.session_state['database_address'] = ""
    if "database_password" not in st.session_state:
        st.session_state['database_password'] = ""

    st.text_input(label="project's address",key="dbaddr")
    st.text_input(label="project's password",type="password",key="dbpass")
    
    if st.button(label="Save"):
        if len(st.session_state.get("dbaddr")) < 1 and len(st.session_state.get("dbpass")) < 1:
            st.session_state.clear()
            st.error("Unable to add Supabase project's info..")
            sleep(2.5)
        else:
            write_db_info_dotenv(address=st.session_state.get("dbaddr"),password=st.session_state.get("dbpass"))
            st.session_state.clear()
            st.success("Successfully added Supabase project's info!!")
            sleep(2.5)
            return True