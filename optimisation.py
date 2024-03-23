import pandas as pd
import numpy as np
from scipy.optimize import minimize

# Déclaration des variables
WEIGHT = "WEIGHT"
WEIGHTED_RETURNS = "WEIGHTED_RETURNS"
RETURNS = "RETURNS"
POSITION = "POSITION"
SHORT, LONG = "SHORT", "LONG"

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
            nb_long_shares = len(portfolio[portfolio[POSITION] == LONG].dropna())
            nb_short_shares = len(portfolio[portfolio[POSITION] == SHORT].dropna())
            long_weight = 1 / nb_long_shares if nb_long_shares != 0 else 0
            short_weight = - 1 / nb_short_shares if nb_short_shares != 0 else 0
            portfolio.loc[portfolio[POSITION] == LONG, WEIGHT] = long_weight
            portfolio.loc[portfolio[POSITION] == SHORT, WEIGHT] = short_weight

            portfolio[WEIGHTED_RETURNS] = portfolio[RETURNS] * portfolio[WEIGHT]
            weighted_portfolios[RV] = portfolio
            if nb_short_shares == 0 : #and "-" in RV : 
                print(f"Long ptf : {RV}, nb long = {nb_long_shares}, nb short = {nb_short_shares} -> {round(np.sum(portfolio[WEIGHT]))}")
            # if nb_short_shares !=0 : print(f"Long/short ptf : {RV}, nb long = {nb_long_shares}, nb short = {nb_short_shares}-> {round(np.sum(portfolio[WEIGHT]))}")
        return weighted_portfolios
        # R2_V2-V1
    
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
                returns_dict[key] = returns_dict[key].dropna(axis=1, how='all')
                # la ligne précédente sert a éviter un msg d'erreur inutile :)  
                returns_dict[key] = pd.concat([returns_dict[key], new_data], ignore_index=True)
        return returns_dict