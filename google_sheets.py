import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ==========================================
# CONNEXION
# ==========================================
def get_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=scope )

    return gspread.authorize(creds)

def load_sheet(name_sheet):
    client = get_client()
    sheet = client.open( name_sheet ).sheet1
    return sheet
    
def load_dt( spreadsheet_name):
    sheet = load_sheet( spreadsheet_name )
    records = sheet.get_all_records()
    return pd.DataFrame(  records  )

#def load_df(sheet):
#    data = sheet.get_all_records()
#    return pd.DataFrame(data)    
    
def append_row( sheet_name, row):
    sheet = load_sheet(sheet_name)
    sheet.append_row( row ) 
    
def delete_row( sheet_name, row_number):
    sheet = load_sheet(sheet_name)
    sheet.delete_rows(   row_number )    