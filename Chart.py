from datetime import datetime, timedelta, time
from plotly.subplots import make_subplots
from truedata_ws.websocket.TD import TD
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import requests
import pickle
import os

st.set_page_config(layout="wide")

github_session = requests.Session()
github_session.auth = ('Zech123as', "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")
Data = pickle.loads(github_session.get("https://raw.githubusercontent.com/Zech123as/Project-1/main/Expiry_Dict.pkl").content)
print(Data)

@st.cache(allow_output_mutation=True)
def Truedata_login(hash_funcs = {TD : id}):
	td_obj = TD('wssand041', 'sandeep041', live_port=None)
	return td_obj

td_obj = Truedata_login()

percent_complete = Max_profit = j = k = 0

Expiry_Date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

while Expiry_Date.strftime("%A") != "Thursday":
	Expiry_Date = Expiry_Date - timedelta(days = 1)

ST_Form_1 = st.sidebar.form("St_form_1")
ST_Form_2 = st.sidebar.form("St_form_2")

my_bar = st.progress(0)

Index_Name = ST_Form_1.radio("Select Index", ("NIFTY BANK", "NIFTY 50"))
N = ST_Form_1.slider("Select Expiry Distance", min_value = 0, max_value = 40, value = 0)

ST_Form_1.form_submit_button("Submit")

if Index_Name == "NIFTY 50":
	Symbol_Name, Index_Dist, Lot_Size = "NIFTY", 50, 50
elif Index_Name == "NIFTY BANK":
	Symbol_Name, Index_Dist, Lot_Size = "BANKNIFTY", 100, 25
else:
	print("Incorrect Index Name")

end_time_input = Expiry_Date - timedelta(days = N*7)

if end_time_input == datetime(2021, 11, 4):
	N = N+1
	end_time_input = Expiry_Date - timedelta(days = N*7)

IndexCSV  =  pd.DataFrame(td_obj.get_historic_data(Index_Name, duration='7 D', bar_size='EOD',   end_time=end_time_input))

Expiry =  IndexCSV.time[len(IndexCSV)-1]

st.write(Expiry, Expiry.strftime("%A"))

Entry_Date, Exit_Date = ST_Form_2.select_slider("Entry & Exit Date Inputs", options = IndexCSV.time, value = (IndexCSV.time[0], IndexCSV.time[len(IndexCSV.time)-1]), format_func = lambda x: x.date())

Time_Input = ST_Form_2.slider("Entry & Exit Time Inputs", min_value = time(9, 15), max_value = time(15, 30), value = (time(9, 30), time(15, 30)), step = timedelta(minutes = 15))

Entry_Time = timedelta( hours=list(Time_Input)[0].hour, minutes = list(Time_Input)[0].minute )
Exit_Time  = timedelta( hours=list(Time_Input)[1].hour, minutes = list(Time_Input)[1].minute )

Indexcsv2 = pd.DataFrame(td_obj.get_historic_data(Index_Name, duration='7 D', bar_size='1 min', end_time=end_time_input))
Indexcsv2 = Indexcsv2.drop_duplicates(subset = ['time']).set_index('time').reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
Indexcsv2['c'] = Indexcsv2['c'].ffill().bfill()
Indexcsv2['o'].fillna(Indexcsv2['c'], inplace=True)

Index_Entry = Indexcsv2.o[Entry_Date + Entry_Time]
Index_Exit   = Indexcsv2.c[Exit_Date + Exit_Time]

Index_Range_Min, Index_Range_Max = int((Indexcsv2["o"].min()/100)-1)*100, int((Indexcsv2["o"].max()/100)+2)*100

fig = go.Figure(layout = go.Layout(yaxis=dict(domain=[0, 0.69]), yaxis2=dict(domain=[0.7, 1], range=[Index_Range_Min, Index_Range_Max])))

Smbl_exp  =  str(Expiry.year - 2000) + str(Expiry.month).zfill(2) + str(Expiry.day).zfill(2)

ce_atm = (round(Indexcsv2.o[Entry_Date + Entry_Time]//Index_Dist)-0)*Index_Dist
pe_atm = (round(Indexcsv2.o[Entry_Date + Entry_Time]//Index_Dist)+1)*Index_Dist

Sell_Dist = ST_Form_2.slider("Sell Distance", min_value = -15, max_value = 40, value = (-15, 20))

ST_Form_2.form_submit_button("Submit")

Progress_Strart_time = datetime.now().replace(microsecond=0)

while Entry_Date + timedelta(days = k) != Exit_Date:
	
	Date_Divider    = Entry_Date + timedelta(days=k+1, hours=9, minutes=7)
	Date_Divider_DF = pd.DataFrame({"Index_Time": [Date_Divider, Date_Divider], "Index_Value": [Index_Range_Min, Index_Range_Max]})
	
	fig.add_trace(go.Scatter(x=Date_Divider_DF["Index_Time"], y = Date_Divider_DF["Index_Value"], name = "Index Test", yaxis="y2", mode='lines', line=dict(color='#bab6b6'), line_width=0.7, showlegend = False))
	fig.add_vline(x= Date_Divider, line_width=0.7, line_dash="solid", line_color="#bab6b6")
	
	k = k + 1

for i in range((Sell_Dist)[0], (Sell_Dist)[1]+1, 1):
	
	Final_DF = pd.DataFrame()
	
	ce_sell_dist, pe_sell_dist = i, -1*i
	
	ce_sell = pd.DataFrame(td_obj.get_historic_data(Symbol_Name + Smbl_exp + str(ce_atm + ce_sell_dist*Index_Dist) + 'CE', duration='7 D', bar_size='1 min', end_time=end_time_input))
	ce_sell = ce_sell.drop_duplicates(subset = ['time']).set_index('time').reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
	ce_sell['c'] = ce_sell['c'].ffill().bfill()
	ce_sell['o'].fillna(ce_sell['c'], inplace=True)
	
	pe_sell = pd.DataFrame(td_obj.get_historic_data(Symbol_Name + Smbl_exp + str(pe_atm + pe_sell_dist*Index_Dist) + 'PE', duration='7 D', bar_size='1 min', end_time=end_time_input))
	pe_sell = pe_sell.drop_duplicates(subset = ['time']).set_index('time').reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
	pe_sell['c'] = pe_sell['c'].ffill().bfill()
	pe_sell['o'].fillna(pe_sell['c'], inplace=True)
	
	ce_sell_entry, pe_sell_entry = ce_sell.o[Entry_Date + Entry_Time], pe_sell.o[Entry_Date + Entry_Time]
	ce_sell_exit , pe_sell_exit  = ce_sell.c[Exit_Date + Exit_Time]  , pe_sell.c[Exit_Date + Exit_Time]
	
	Final_DF['Change' + str(i)] = (ce_sell_entry + pe_sell_entry) - (ce_sell['o'] + pe_sell['o'])
	Final_DF["CE_SELL"] = "CE  (" + str(round(ce_sell_entry)).rjust(5) + " |" + ce_sell['o'].round().astype(int).astype(str).str.rjust(5) + " )"
	Final_DF["PE_SELL"] = "PE  (" + str(round(pe_sell_entry)).rjust(5) + " |" + pe_sell['o'].round().astype(int).astype(str).str.rjust(5) + " )"
	Final_DF["FINAL"] = Final_DF["CE_SELL"] + "    |    " + Final_DF["PE_SELL"]
	
	if Final_DF['Change' + str(i)].max() > Max_profit:
		Max_profit = Final_DF['Change' + str(i)].max()
	
	fig.add_trace(go.Scatter(x=Final_DF.index, y=Final_DF["Change"+str(i)], legendgrouptitle_text = (str(int(i/5)) + "Group"), legendgroup= int(i/5), customdata = Final_DF["FINAL"], name = str(i).rjust(4), hovertemplate='Profit: (%{y:5d} )   |   %{customdata}'))#, visible='legendonly'))
	
	percent_complete = percent_complete + 1
	
	my_bar.progress((percent_complete)/len(range((Sell_Dist)[0], (Sell_Dist)[1]+1, 1)))

st.write((datetime.now().replace(microsecond=0) - Progress_Strart_time))

fig.add_trace(go.Scatter(x= Indexcsv2.index, y= Indexcsv2["o"], yaxis="y2", name = Index_Name, line=dict(color='blue'), line_width=0.8, legendrank = 1))

Indexcsv2["Entry_line"] = Index_Entry
fig.add_trace(go.Scatter(x=Indexcsv2.index, y = Indexcsv2["Entry_line"], line=dict(color='red'), line_width=0.5, name = "Index Entry", yaxis="y2", showlegend = False))

Final_DF_2 = pd.DataFrame()
Final_DF_2["Index"] = " ( " + (Indexcsv2['o'] - Index_Entry).map('{:+,.2f}'.format) + " )" + (Indexcsv2['o']).round().astype(int).map('{:,}'.format).str.rjust(7)
Final_DF_2["Max_profit_column"] = int((Max_profit/100) + 1)*100

fig.add_trace(go.Scatter(x=Final_DF_2.index, y = Final_DF_2["Max_profit_column"], customdata = Final_DF_2["Index"], name = Index_Name, hovertemplate='%{customdata}', legendrank = 2, line=dict(color='red'), line_width=0.5, showlegend = False))

fig.update_xaxes(showspikes=True, spikedash = "solid", spikecolor="red", spikesnap="hovered data", spikemode="across", spikethickness = 0.5)
fig.update_xaxes(rangebreaks=[dict(bounds=[15.75, 9], pattern="hour")])
fig.update_xaxes(rangeslider_visible=True)
fig.update_xaxes(showgrid=False)

fig.update_yaxes(showgrid=True, gridcolor='#e0e0e0', zerolinecolor = '#989c9b')

fig.update_layout(height = 1200, hovermode = "x unified")

st.plotly_chart(fig, use_container_width = True, config={'displayModeBar': True})
