import pandas as pd
import numpy as np
from scipy.optimize import minimize

#Déclaration des variables
WEIGHT = "WEIGHT"
WEIGHTED_RETURNS = "WEIGHTED_RETURNS"
RETURNS = "RETURNS"

class Optimisation:
    def __init__(self, portfolios: dict):
        """
        Initialize PortfolioPerformance object with a dictionary of portfolios.

        :param portfolios: Dictionary containing portfolios for each date.
        """
        self.portfolios = portfolios

    @staticmethod
    def get_equal_weighted(date_portfolios: dict) -> dict:
        weighted_portfolios = {}
        for RV, portfolio in date_portfolios.items():
            nb_shares = len(portfolio.dropna())
            weight = 1 / nb_shares
            portfolio[WEIGHT] = weight
            portfolio[WEIGHTED_RETURNS] = portfolio[RETURNS] * portfolio[WEIGHT]
            weighted_portfolios[RV] = portfolio
        return weighted_portfolios
    
    @staticmethod
    def get_date_returns(portfolio: pd.DataFrame) -> float:
        return portfolio[WEIGHTED_RETURNS].sum()
    
    def get_full_returns(self) -> dict:
        returns_dict = {}
        for date, date_portfolios in self.portfolios.items():
            date_portfolios = self.get_equal_weighted(date_portfolios)
            for key, portfolio_df in date_portfolios.items():
                full_returns = self.get_date_returns(portfolio_df)
                if key not in returns_dict:
                    returns_dict[key] = pd.DataFrame(columns=['Date', 'Full_Returns'])
                new_data = pd.DataFrame({'Date': [date], 'Full_Returns': [full_returns]})
                returns_dict[key] = pd.concat([returns_dict[key], new_data], ignore_index=True)
        return returns_dict