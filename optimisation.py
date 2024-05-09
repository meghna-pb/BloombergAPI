import pandas as pd
import numpy as np

from signals import RETURNS, WEIGHT, WEIGHTED_RETURNS, POSITION, LONG, SHORT, RETURNS
from data import VOLATILITY, EXPECTED_RETURNS, RFR

DATES = "DATES"
WEIGHTED_VOLATILITY = "WEIGHTED_VOLATILITY"


class Optimisation:
    def __init__ (self, returns_portfolios:dict, volume_portfolios:dict):
        """
        Initialize the Optimisation class to manage portfolio weights and calculations based on different strategies.
        
        :param returns_portfolios: Dictionary containing returns data for various portfolios.
        :param volume_portfolios: Dictionary containing volume data for various portfolios.
        """
        self.returns_portfolios = returns_portfolios
        self.volume_portfolios = volume_portfolios

        
    @staticmethod
    def get_equal_weight(portfolios:dict) -> dict:
        """
        Assign equal weights to long and short positions within each portfolio.
        
        :param portfolios: Dictionary of portfolio data.
        
        :return: Updated dictionary with equal weights assigned to long and short positions.
        """
        for date in portfolios.keys():  
            for name, ptf in portfolios[date].items():
                nb_long_shares = len(ptf[ptf[POSITION] == LONG].dropna())
                nb_short_shares = len(ptf[ptf[POSITION] == SHORT].dropna())
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] =  1 / nb_long_shares if nb_long_shares != 0 else 0
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = - 1 / nb_short_shares if nb_short_shares != 0 else 0
                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
                ptf[WEIGHTED_VOLATILITY] = ptf[VOLATILITY] * ptf[WEIGHT]
        return portfolios
    
    @staticmethod
    def get_scaling_weight(portfolios: dict) -> dict:
        """
        Adjust weights inversely proportional to the volatility of each position in the portfolio.
        
        :param portfolios: Dictionary of portfolio data.
        
        :return: Updated dictionary with scaled weights based on volatility.
        """
        for date in portfolios.keys():
            for name, ptf in portfolios[date].items():
                ptf[WEIGHT] = 1 / ptf[VOLATILITY]
        
                long_weights = ptf[ptf[POSITION] == LONG][WEIGHT]
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] = long_weights / long_weights.sum()
                short_weights = ptf[ptf[POSITION] == SHORT][WEIGHT]
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = -short_weights / short_weights.sum()

                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
                ptf[WEIGHTED_VOLATILITY] = ptf[VOLATILITY] * ptf[WEIGHT]
        return portfolios
    
    @staticmethod
    def get_sharpe_weight(portfolios: dict) -> dict:
        """
        Assign weights based on the Sharpe ratio, considering both expected returns and volatility.
        
        :param portfolios: Dictionary of portfolio data.
        
        :return: Updated dictionary with weights calculated from Sharpe ratios.
        """
        for date in portfolios.keys():
            for name, ptf in portfolios[date].items():
                sharpe_ratios = (ptf[EXPECTED_RETURNS] - ptf[RFR]) / (ptf[VOLATILITY] + 1e-6)
                sharpe_ratios = sharpe_ratios.replace([np.inf, -np.inf, np.nan], 0)

                long_weights = sharpe_ratios[ptf[POSITION] == LONG]
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] = long_weights / long_weights.sum()
                short_weights = sharpe_ratios[ptf[POSITION] == SHORT]
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = -(abs(short_weights) / abs(short_weights).sum())

                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
                ptf[WEIGHTED_VOLATILITY] = ptf[VOLATILITY] * ptf[WEIGHT]
        return portfolios
    
    
    @staticmethod
    def __get_dated_results(dated_portfolio: pd.DataFrame) -> float:
        """
        Calculate the aggregated weighted returns and volatility for a given portfolio on a specific date.
        
        :param dated_portfolio: DataFrame representing a single portfolio on a specific date.
        
        :return: Tuple containing summed weighted returns and summed weighted volatility.
        """
        return dated_portfolio[WEIGHTED_RETURNS].sum(), dated_portfolio[WEIGHTED_VOLATILITY].sum()
    
    def get_full_results(self, portfolios:dict) -> dict:
        """
        Aggregate results across all dates for each portfolio, computing overall returns and volatility.
        
        :param portfolios: Dictionary of portfolios, keyed by date and portfolio name.
        
        :return: Dictionary keyed by portfolio name with DataFrames containing cumulative returns and volatility data.
        """
        dict_returns = {}
        for date, ptf in portfolios.items():
            for key, portfolio_df in ptf.items():
                full_returns, full_volatility = self.__get_dated_results(portfolio_df)
                if key not in dict_returns:
                    dict_returns[key] = pd.DataFrame(columns=[DATES, RETURNS, VOLATILITY])
                new_data = pd.DataFrame({DATES: [date], RETURNS: [full_returns], VOLATILITY: [full_volatility]})
                dict_returns[key] = dict_returns[key].dropna(axis=1, how='all')
                dict_returns[key] = pd.concat([dict_returns[key], new_data], ignore_index=True)
        return dict_returns

