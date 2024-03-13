import pandas as pd
import matplotlib.pyplot as plt

from data import Data
from signal_1 import Signal
import optimisation


data = Data("Data").get_data()
#for date, df in data.items():
#    print(f"For date: {date}")
#    print(df)
    
# concatenated_df = pd.concat(data.values(), axis=0)
# grouped_df = concatenated_df.loc['RETURNS']
# plt.figure(figsize=(10, 6))
# grouped_df.plot(kind='line')
# plt.title('Returns for Each Ticker Across Dates')
# plt.xlabel('Date')
# plt.ylabel('Returns')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()


sig = Signal(data)

##############################
### Les lignes en com ici ne vont plus fonctionner avec ma nouvelle version de create_portfolio
# test, exemple_date = sig.create_portfolios(3,2)
# print(test[exemple_date])
# print(type(test[exemple_date]["RETURNS_1"]))
# dict_returns, dict_volume, exemple_date = sig.create_portfolios(3,2)
#print(dict_returns[exemple_date]["R1"])
###############################

###### Test intersection 
intersec, exemple_date = sig.create_intersections(3, 2)
#print(intersec[exemple_date])
portfolio_test = intersec[exemple_date]
print(portfolio_test)

###### Test pondération equi : poids et rendements 
#portfolio_test_2 = optimisation.get_equal_weighted(portfolio_test)
#print(portfolio_test_2)
#return_test = optimisation.get_date_returns(portfolio_test)
#print(return_test)

###### Test calcul rendements sur toute les périodes : (marche pas)
#portfolio_test = intersec[exemple_date]
#optimisation.get_full_returns(portfolio_test)