import pandas as pd

from performance import Performance
from data import Data

DATE = "date" # maintenabilité du code + on ne sait pas comment la colonne s'appelle dans bloom
VOLUME = "PX_VOLUME" # Pourquoi ? 

class Signal:
    def __init__(self, data, risk_free_rate=0.02):
        """
        Initializes the Signal object.

        :param bench: DataFrame with benchmark data.
        :param portfolio: DataFrame with portfolio data including 'ticker', 'weight', 'PX_LAST', and other necessary columns.
        :param risk_free_rate: Risk-free rate, default is 2%.
        """
        self.data = data
        # self.performance = Performance(bench, portfolio, risk_free_rate)
        self.portfolios = {}
        

    def create_portfolios(self, n_returns, m_volume):
        """
        Creates n return portfolios and m volume portfolios for each date 
        :param n_returns: Number of return portfolios to create for each date.
        :param m_volume: Number of volume portfolios to create for each date.
        :return: A dictionary containing the return and volume portfolios for each date.
        """

        # For each date, create the portfolios
        for date, date_data in self.data.items():            
            self.portfolios[date] = {}
            sorted_by_returns = date_data.sort_values(by='RETURNS', axis=1, ascending=False)
            sorted_by_volume = date_data.sort_values(by=VOLUME, axis=1, ascending=False)

            # Create return portfolios for this date
            self.portfolios[date]['RETURNS'] = [sorted_by_returns.iloc[i::n_returns] for i in range(min(n_returns, len(sorted_by_returns)))]
            
            # Create volume portfolios for this date
            self.portfolios[date][VOLUME] = [sorted_by_volume.iloc[i::m_volume] for i in range(min(m_volume, len(sorted_by_volume)))]

        return self.portfolios, date # J'ai rajouté date juste pour pouvoir tester :) 
    