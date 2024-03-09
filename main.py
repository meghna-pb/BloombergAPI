import pandas as pd
import matplotlib.pyplot as plt

from data import Data

# J'ai fait pas mal de modif dans la classe data pour integrer un peu ce que j'avais fait ce matin 
# J'ai testé le graphiques, j'ai exactement les mêmes résultats
# Je t'ai laisser ta version dans le folder archive si tu préfères


data = Data("Data")
results = data.get_data() # data.calculate_returns()

#for date, df in results.items():
#    print(f"For date: {date}")
#    print(df)
    
concatenated_df = pd.concat(results.values(), axis=0)
grouped_df = concatenated_df.loc['RETURNS']
plt.figure(figsize=(10, 6))
grouped_df.plot(kind='line')
plt.title('Returns for Each Ticker Across Dates')
plt.xlabel('Date')
plt.ylabel('Returns')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
