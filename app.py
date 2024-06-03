import streamlit as st
from tools import run_app
from data import Data
from datetime import datetime

st.title("Bloomberg API - Master 272")
st.write("Meghna BHAUGEERUTTY, Caroline KIRCH")

ind_choice = st.selectbox('Select the index on which to apply the strategy', 
             ['RIY Index', 'Other'])
risk_free_rate = st.slider('Choose the risk free rate', min_value=0.01, value=0.02, max_value=1.0)
col1, col2 = st.columns(2)
J = col1.number_input('Choose the period of returns (in months) ', min_value=2, step = 1,value =4)
K =  col2.number_input('Choose the holding period (in months)', min_value=2, step = 1, value =12)
col3, col4 = st.columns(2)
n =  col3.number_input('Choose the number of returns portfolios', min_value=1, step = 1, value = 10)
m = col4.number_input('Choose the number of volume portfolios ', min_value=1, step = 1, value = 3)

if ind_choice != 'RIY Index':
    ind_ticker = st.text_input('Input the ticker', value="SPX Index")
    col1, col2 = st.columns(2)
    start_dt = col1.date_input("Choose the start date : ", max_value =  datetime(2024, 1, 28),  value=datetime(2024, 1, 28), )
    end_dt = col2.date_input("Choose the end date : ", max_value = datetime.now())
    data = Data(path="", J=J, risk_free_rate=risk_free_rate, index_ticker =ind_ticker, 
                 start_date = start_dt, end_date = end_dt) 

else:
    bbg_or_xl = st.radio('Do you want to fetch the data from Bloomberg or our Excel extract?', 
             ['Excel', 'Bloomberg'], 
            horizontal=True )
    if bbg_or_xl == "Bloomberg":
        col1, col2 = st.columns(2)
        start_dt = col1.date_input("Choose the start date : ", max_value =  datetime(2024, 1, 28), value=datetime(2024, 1, 28))
        end_dt = col2.date_input("Choose the end date : ", max_value = datetime.now())
        data = Data(path="", J=J, risk_free_rate=risk_free_rate, 
                 start_date = start_dt, end_date = end_dt) 
    else:
        data = Data(path="Data", J=J, risk_free_rate=risk_free_rate) 

pond_choice = st.selectbox('Choose the weighting scheme for the strategy', 
             ['Equi-weighted', '1/Volatility', 'Volume', 'Volume x price', 
             # "Best weighting method"
              ])
dict_pond = {'Equi-weighted':'equi', '1/Volatility':'vol', 'Volume':'volume', 'Volume x price':'volumexprice', "Best weighting method":"best"}
pond = dict_pond[pond_choice]

col1, col2 = st.columns(2)
viewer = col1.selectbox('Select the graph you want', 
                    ["Performance", "Histogram of metrics" ,"Cumulated performance" ], 
                    )

metric = col2.selectbox('Select the metric', 
                    ["Overall Performance" ,"Annualized Performance","Monthly Volatility" ,
                     "Annualized Volatility","Maximum Drawdown","Sharpe Ratio" ,"Tracking Error" ,"t-stat" ])
view_choice = {"Histogram of metrics":"hist" ,"Performance":"perf","Cumulated performance": "cumulative_v"}

if st.button('Show results'):
    fig, df = run_app(data, K, n, m, pond, view_choice[viewer], method=metric)
    df_r = df.round(2)
    st.plotly_chart(fig)
    st.dataframe(df_r)

