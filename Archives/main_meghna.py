import pandas as pd
from data_meghna import Data
import matplotlib.pyplot as plt


data = Data("Data")
result = data.calculate_returns()
# for date, df in result.items():
#     print(f"For date: {date}")
#     print(df)
    
concatenated_df = pd.concat(data.result_dict.values(), axis=0)
grouped_df = concatenated_df.loc['returns']
plt.figure(figsize=(10, 6))
grouped_df.plot(kind='line')
plt.title('Returns for Each Ticker Across Dates')
plt.xlabel('Date')
plt.ylabel('Returns')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()