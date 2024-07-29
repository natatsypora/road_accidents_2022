import streamlit as st
import pandas as pd
import json 
import requests


# Define the Google Drive file URL
# 1.csv 'teunot_2022_2.csv'
url = 'https://drive.google.com/file/d/1IeusRkjtr-Y-9LLI3AWwXvDxVCzh9fxJ/view?usp=sharing'
# 2.geojson 'data_geojson_nafot.json'
url_2 = 'https://drive.google.com/file/d/1C36bGukGHwZuzJ-tEHLB7XTFn8okfJoI/view?usp=drive_link'
# 3.xlsx 'teunot_by_month_type2022.xlsx'
url_3 ='https://docs.google.com/spreadsheets/d/1U9GNdGpxm0rEo7WmE3Y9dKoDVlr7n5ye/edit?usp=sharing'

# Define the function to get the file path and download the file
def get_path_from_url(url):
    path = url.split('/')[-2]
    file_path = 'https://drive.google.com/uc?export=download&id=' + path
    return file_path
# Define the function to read the csv
@st.cache_data
def read_csv_data(url):
    file_path = get_path_from_url(url)
    df = pd.read_csv(file_path)
    return df
#Define the function to read the excel
@st.cache_data
def read_excel_data(url):
    file_path = get_path_from_url(url)
    df = pd.read_excel(file_path, sheet_name=None, index_col=0)
    return df
#Define the function to read the json   
@st.cache_data
def load_json_data(url):
    file_url = get_path_from_url(url)
    response = requests.get(file_url)
    data = json.loads(response.text)
    return data

#------------------------------------------------------------------------------ 
# Define the function to show the information about the dataframe  
def show_info(df):
    """Return a dataframe ( descriptive statistics that summarize the dataset,
    including unique, missing  and zero values)."""

    # get the desired statistics using the built-in methods of pandas dataframe
    res = df.agg(["count", "nunique"]).T
    res["missing"] = df.isna().sum()
    res["% missing"] = round(res["missing"] / len(df) * 100, 2)
    res.insert(0, "data_type", df.dtypes)
    res['zero'] = (df == 0).sum(axis=0)
    res['%zero'] = round(res['zero']/df.shape[0]*100, 2)

    res.index.name = "col_name"
    res.reset_index(inplace=True)

    return res.replace(0, '-')
    
#------------------------------------------------------------------------------
# # Define the sort arrays for the index
sort_week = ['ראשון','שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']

sort_month = ['ינואר', 'פברואר', 'מרס', 'אפריל', 'מאי', 'יולי', 'יוני',
              'אוגוסט', 'ספטמבר',  'אוקטובר', 'נובמבר',  'דצמבר'] 

sort_month_en =['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December']   