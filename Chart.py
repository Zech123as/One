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





Index_csv_1 = Main_Dict["Index_csv_1"]

Expiry =  Index_csv_1.time[len(Index_csv_1)-1]

st.write(f"{Expiry}, {Expiry.strftime("%A")}")

ST_Form_2 = st.sidebar.form("St_form_2")

Entry_Date, Exit_Date = ST_Form_2.select_slider("Entry & Exit Date Inputs", options = Index_csv_1.time, value = (Index_csv_1.time[0], Index_csv_1.time[len(Index_csv_1.time)-1]), format_func = lambda x: x.date())
Time_Input = ST_Form_2.slider("Entry & Exit Time Inputs", min_value = time(9, 15), max_value = time(15, 30), value = (time(9, 30), time(15, 30)), step = timedelta(minutes = 15))
Sell_Dist = ST_Form_2.slider("Sell Distance", min_value = -15, max_value = 40, value = (-15, 20))

ST_Form_2.form_submit_button("Submit")

Entry_Time = timedelta( hours=list(Time_Input)[0].hour, minutes = list(Time_Input)[0].minute )
Exit_Time  = timedelta( hours=list(Time_Input)[1].hour, minutes = list(Time_Input)[1].minute )

Index_csv_2 = Main_Dict["Index_csv_2"]

Index_Entry = Index_csv_2.o[Entry_Date + Entry_Time]
Index_Exit  = Index_csv_2.o[Exit_Date  + Exit_Time ]

Index_Range_Min, Index_Range_Max = int((Index_csv_2["o"].min()/100)-1)*100, int((Index_csv_2["o"].max()/100)+2)*100

fig = go.Figure(layout = go.Layout(yaxis=dict(domain=[0, 0.69]), yaxis2=dict(domain=[0.7, 1], range=[Index_Range_Min, Index_Range_Max])))

ce_atm = (round(Index_csv_2.o[Entry_Date + Entry_Time]//Index_Dist)-0)*Index_Dist
pe_atm = (round(Index_csv_2.o[Entry_Date + Entry_Time]//Index_Dist)+1)*Index_Dist

st.write(ce_atm, pe_atm)
#percent_complete = Max_profit = j = k = 0
