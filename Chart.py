from datetime import datetime, timedelta, time
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import requests
import pickle
import os

st.set_page_config(layout="wide")

github_session = requests.Session()
github_session.auth = ('Zech123as', "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")

ST_Form_1 = st.sidebar.form("St_form_1")

Index_Name = ST_Form_1.radio("Select Index", ("NIFTY BANK", "NIFTY 50"))
Expiry_Dist = ST_Form_1.slider("Select Expiry Distance", min_value = 0, max_value = 40, value = 0)

ST_Form_1.form_submit_button("Submit")

if Index_Name == "NIFTY 50":
	Index_Dist, Lot_Size = 50, 50
elif Index_Name == "NIFTY BANK":
	Index_Dist, Lot_Size = 100, 25
else:
	print("Incorrect Index Name")

end_time_input = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

while end_time_input.strftime("%A") != "Thursday":
	end_time_input = end_time_input - timedelta(days = 1)

end_time_input = end_time_input - timedelta(days = Expiry_Dist*7)

Data = pickle.loads(github_session.get(f"https://raw.githubusercontent.com/Zech123as/One/main/Expiry_Data/Expiry_Dict_{end_time_input.date()}.pkl").content)

Main_Dict = Data[Index_Name]

st.write(Main_Dict.keys())

#ST_Form_2 = st.sidebar.form("St_form_2")

#percent_complete = Max_profit = j = k = 0
