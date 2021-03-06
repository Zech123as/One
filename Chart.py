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
github_session.auth = ('Zech123as', "50fa7jl6Autxj+2Q1T6Zei6lB4xLnZX+RNi9xYJQeUw")

ST_Form = st.sidebar.form("St_form")

Index_Name = ST_Form.radio("Select Index", ("NIFTY BANK", "NIFTY 50"))
Expiry_Dist = ST_Form.slider("Select Expiry Distance", min_value = 0, max_value = 40, value = 0)

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






Index_csv_1 = Main_Dict["Index_csv_1"]

Expiry =  Index_csv_1.time[len(Index_csv_1)-1]

Entry_Date, Exit_Date = ST_Form.select_slider("Entry & Exit Date Inputs", options = Index_csv_1.time, value = (Index_csv_1.time[0], Index_csv_1.time[len(Index_csv_1.time)-1]), format_func = lambda x: x.date())
Time_Input = ST_Form.slider("Entry & Exit Time Inputs", min_value = time(9, 15), max_value = time(15, 30), value = (time(9, 30), time(15, 30)), step = timedelta(minutes = 15))
Buy_Lots  = ST_Form.slider("No of Buy Lots", min_value = 0, max_value = 15, value = 5)
Buy_Dist  = ST_Form.slider("Buy Distance", min_value = 0, max_value = 30, value = 15)
Sell_Dist = ST_Form.slider("Sell Distance", min_value = -15, max_value = 40, value = (-15, 20))

ST_Form.form_submit_button("Submit")

Entry_Time = timedelta( hours=list(Time_Input)[0].hour, minutes = list(Time_Input)[0].minute )
Exit_Time  = timedelta( hours=list(Time_Input)[1].hour, minutes = list(Time_Input)[1].minute )

Index_csv_2 = Main_Dict["Index_csv_2"].reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')

Index_Entry = Index_csv_2.o[Entry_Date + Entry_Time]
Index_Exit  = Index_csv_2.o[Exit_Date  + Exit_Time ]

Index_Range_Min, Index_Range_Max = int((Index_csv_2["o"].min()/100)-1)*100, int((Index_csv_2["o"].max()/100)+2)*100

fig = go.Figure(layout = go.Layout(yaxis2=dict(domain=[0, 0.29], range=[Index_Range_Min, Index_Range_Max]), yaxis=dict(domain=[0.3, 1])))

ce_atm = (round(Index_csv_2.o[Entry_Date + Entry_Time]//Index_Dist)-0)*Index_Dist
pe_atm = (round(Index_csv_2.o[Entry_Date + Entry_Time]//Index_Dist)+1)*Index_Dist

Max_Profit = j = k = 0




while Entry_Date + timedelta(days = k) != Exit_Date:
	
	Date_Divider    = Entry_Date + timedelta(days=k+1, hours=9, minutes=7)
	Date_Divider_DF = pd.DataFrame({"Index_Time": [Date_Divider, Date_Divider], "Index_Value": [Index_Range_Min, Index_Range_Max]})
	
	fig.add_trace(go.Scatter(x=Date_Divider_DF["Index_Time"], y = Date_Divider_DF["Index_Value"], name = "Index Test", yaxis="y2", mode='lines', line=dict(color='#bab6b6'), line_width=0.7, showlegend = False))
	fig.add_vline(x= Date_Divider, line_width=0.7, line_dash="solid", line_color="#bab6b6")
	
	k = k + 1

for i in range((Sell_Dist)[0], (Sell_Dist)[1]+1, 1):
	
	Final_DF = pd.DataFrame()
	
	ce_sell_dist, pe_sell_dist = i, -i
	
	ce_sell = Main_Dict[str(ce_atm + ce_sell_dist*Index_Dist) + 'CE'].reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
	pe_sell = Main_Dict[str(pe_atm + pe_sell_dist*Index_Dist) + 'PE'].reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
	
	ce_sell_entry, pe_sell_entry = ce_sell.o[Entry_Date + Entry_Time], pe_sell.o[Entry_Date + Entry_Time]
	ce_sell_exit , pe_sell_exit  = ce_sell.o[Exit_Date + Exit_Time]  , pe_sell.o[Exit_Date + Exit_Time]
	
	
	ce_buy_dist, pe_buy_dist = i + Buy_Dist, -i-Buy_Dist
	
	ce_buy = Main_Dict[str(ce_atm + ce_buy_dist*Index_Dist) + 'CE'].reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
	pe_buy = Main_Dict[str(pe_atm + pe_buy_dist*Index_Dist) + 'PE'].reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
	
	ce_buy_entry, pe_buy_entry = ce_buy.o[Entry_Date + Entry_Time], pe_buy.o[Entry_Date + Entry_Time]
	ce_buy_exit , pe_buy_exit  = ce_buy.o[Exit_Date + Exit_Time]  , pe_buy.o[Exit_Date + Exit_Time]
	
	
	
	Final_DF['Change' + str(i)] = ((ce_sell_entry + pe_sell_entry) - (ce_sell['o'] + pe_sell['o'])) + (((ce_buy['o'] + pe_buy['o']) - (ce_buy_entry + pe_buy_entry))*Buy_Lots)
	
	Final_DF["CE_SELL"] = "CE SELL (" + str(round(ce_sell_entry)).rjust(5) + " |" + ce_sell['o'].round().astype(int).astype(str).str.rjust(5) + " )"
	Final_DF["PE_SELL"] = "PE SELL (" + str(round(pe_sell_entry)).rjust(5) + " |" + pe_sell['o'].round().astype(int).astype(str).str.rjust(5) + " )"
	
	Final_DF["CE_BUY"]  = "CE BUY (" + str(round(ce_buy_entry)).rjust(5) + " |" + ce_buy['o'].round().astype(int).astype(str).str.rjust(5) + " )"
	Final_DF["PE_BUY"]  = "PE BUY (" + str(round(pe_buy_entry)).rjust(5) + " |" + pe_buy['o'].round().astype(int).astype(str).str.rjust(5) + " )"	
	
	Final_DF["FINAL"] = Final_DF["CE_SELL"] + "   |   " + Final_DF["PE_SELL"] + "   |   " + "( " + Final_DF["CE_BUY"] + "   |   " + Final_DF["PE_BUY"] + " ) " + " * " + str(Buy_Lots)
	
	if Final_DF['Change' + str(i)].max() > Max_Profit:
		Max_Profit = Final_DF['Change' + str(i)].max()
	
	#fig.add_trace(go.Scatter(x=Final_DF.index, y=Final_DF["Change"+str(i)], legendgrouptitle_text = (str(int(i/5)) + "Group"), legendgroup= int(i/5), name = str(i).rjust(4), hovertemplate='Profit: (%{y:5d} )'))
	fig.add_trace(go.Scatter(x=Final_DF.index, y=Final_DF["Change"+str(i)], mode = 'lines', legendgrouptitle_text = (str(int(i/5)) + "Group"), legendgroup= int(i/5), customdata = Final_DF["FINAL"], name = str(i).rjust(4), hovertemplate='Profit: (%{y:5d} )   |   %{customdata}'))#, visible='legendonly'))
	
fig.add_trace(go.Scatter(x= Index_csv_2.index, y= Index_csv_2["o"], yaxis="y2", mode='lines', name = Index_Name, line=dict(color='blue'), line_width=0.8, legendrank = 1))

Index_csv_2["Entry_line"] = Index_Entry
fig.add_trace(go.Scatter(x=Index_csv_2.index, y = Index_csv_2["Entry_line"], line=dict(color='red'), line_width=0.5, name = "Index Entry", yaxis="y2", showlegend = False))

Final_DF_2 = pd.DataFrame()
Final_DF_2["Index"] = " ( " + (Index_csv_2['o'] - Index_Entry).map('{:+,.2f}'.format) + " )" + (Index_csv_2['o']).round().astype(int).map('{:,}'.format).str.rjust(7)
Final_DF_2["Max_Profit_column"] = int((Max_Profit/100) + 1)*100

fig.add_trace(go.Scatter(x=Final_DF_2.index, y = Final_DF_2["Max_Profit_column"], customdata = Final_DF_2["Index"], name = Index_Name, hovertemplate='%{customdata}', legendrank = 2, line=dict(color='red'), line_width=0.5, showlegend = False))

fig.update_xaxes(showspikes=True, spikedash = "solid", spikecolor="red", spikesnap="hovered data", spikemode="across", spikethickness = 0.5)
fig.update_xaxes(rangebreaks=[dict(bounds=[15.75, 9], pattern="hour")])
fig.update_xaxes(rangeslider_visible=True)
fig.update_xaxes(showgrid=False)

fig.update_yaxes(showgrid=True, gridcolor='#e0e0e0', zerolinecolor = '#989c9b')

fig.update_layout(title = f'{Expiry.date()}, {Expiry.strftime("%A")}', height = 1000, hovermode = "x")

st.plotly_chart(fig, use_container_width = True, config={'displayModeBar': True})
