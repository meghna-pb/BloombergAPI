from datetime import datetime

from bloomberg import df_PX_LAST, df_PX_VOLUME
from signal_caro import Signal

print(df_PX_LAST)

# test_signal = Signal(df_PX_LAST, df_PX_VOLUME)
# test_returns = test_signal.calculate_returns()

# date = datetime(2024, 1, 1)
# date = "2023-01"
# date = datetime.strptime('2023-01-01', '%Y-%m-%d') 
# date = 6

# test = test_signal.create_portfolios(date, 4, 5)
# print(test)

