import streamlit as st
from main import test_st
from data import Data
from datetime import datetime
st.title("Stratégie d'investissement")
st.write("Bloomberg API - Master 272")


ind_choice = st.selectbox('Select the index on which to apply the strategy', 
             ['RIY Index', 'Other'])
risk_free_rate = st.number_input('Choose the risk free rate', min_value=0.01, value=0.2)
col1, col2, col3, col4 = st.columns(4)
J = col1.number_input('Choose the period of returns ', min_value=2, step = 1,value =3)
K =  col2.number_input('Choose the holding period ', min_value=2, step = 1, value =3)
n =  col3.number_input('Choose the number of returns portfolios', min_value=1, step = 1, value = 7)
m = col4.number_input('Choose the number of volume portfolios ', min_value=1, step = 1, value = 5)

if ind_choice != 'RIY Index':
    ind_ticker = st.text_input('Input the ticker', value="SPX Index")
    col1, col2 = st.columns(2)
    start_dt = col1.date_input("Choose the start date : ", max_value =  datetime(2024, 1, 28))
    end_dt = col2.date_input("Choose the end date : ", max_value =datetime.now())
    data = Data(path="", J=J, risk_free_rate=risk_free_rate, index_ticker =ind_ticker, 
                 start_date = start_dt, end_date = end_dt) 

else:
    bbg_or_xl = st.selectbox('Do you want to fetch the data from Bloomberg or our Excel extract?', 
             ['Excel', 'Bloomberg'])
    if bbg_or_xl == "Bloomberg":
        col1, col2 = st.columns(2)
        start_dt = col1.date_input("Choose the start date : ", max_value =  datetime(2024, 1, 28))
        end_dt = col2.date_input("Choose the end date : ", max_value = datetime.now())
        data = Data(path="", J=J, risk_free_rate=risk_free_rate, 
                 start_date = start_dt, end_date = end_dt) 
    else:
        data = Data(path="Data", J=J, risk_free_rate=risk_free_rate) 

pond_choice = st.selectbox('Choose the weighting method for the strategy', 
             ['Equi-weighted', '1/Volatility', 'Sharpe', 'Volume', 'Volume x price'])
dict_pond = {'Equi-weighted':'equi', '1/Volatility':'vol', 'Sharpe':'sharpe', 'Volume':'volume', 'Volume x price':'volumexprice'}
pond = dict_pond[pond_choice]

col1, col2 = st.columns(2)
viewer = col1.selectbox('Select the graph you want', 
                    ["Histogram of metrics" ,"Performance","Cumulated performance" ])
metric = col2.selectbox('Select the metric', 
                    ["Overall Performance" ,"Annualized Performance","Monthly Volatility" ,
                     "Annualized Volatility","Maximum Drawdown","Sharpe Ratio" ,"Tracking Error" ,"t-stat" ])


view_choice = {"Histogram of metrics":"hist" ,"Performance":"perf","Cumulated performance": "cumulative_v"}
if st.button('Show results'):
    test_st(data, K, n, m, pond, view_choice[viewer], method=metric)
