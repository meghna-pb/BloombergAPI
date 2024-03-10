import pandas as pd
import matplotlib.pyplot as plt

from data import Data
from signal_1 import Signal

# J'ai fait pas mal de modif dans la classe data pour integrer un peu ce que j'avais fait ce matin 
# La sortie est exactement la même + j'ai testé le graphiques, j'ai exactement les mêmes résultats
# Je t'ai laissé ta version dans le folder archives si tu préfères


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
test, exemple_date = sig.create_portfolios(3,2)
print(test[exemple_date])
#print(test[exemple_date]["RETURNS"][0])

# Je comprends vraiment rien a comment c'est construit 

