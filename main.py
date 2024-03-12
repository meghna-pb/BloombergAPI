import pandas as pd
import matplotlib.pyplot as plt

from data import Data
from signal_1 import Signal


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

### Les lignes en com ici vont plus fonctionner avec ma nouvelle version de create_portfolio

# test, exemple_date = sig.create_portfolios(3,2)
# print(test[exemple_date])
# print(type(test[exemple_date]["RETURNS_1"]))

# dict_returns, dict_volume, exemple_date = sig.create_portfolios(3,2)
#print(dict_returns[exemple_date]["R1"])

intersec, exemple_date = sig.create_intersections(3, 2)
print(intersec[exemple_date])



