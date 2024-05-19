import pandas as pd
import numpy as np

from signals import RETURNS, VOLUME, PX_LAST, WEIGHT, WEIGHTED_RETURNS, POSITION, LONG, SHORT, RETURNS, VOLATILITY, RFR

DATES = "DATES"


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
        return portfolios
        
    @staticmethod
    def get_volume_weight(portfolios: dict) -> dict:
        """
        Adjust weights based on the trading volume of each position in the portfolio, separately for long and short positions.
    
        :param portfolios: Dictionary of portfolio data.
    
        :return: Updated dictionary with weights based on trading volume for both long and short positions.
        """
        for date in portfolios.keys():
            for name, ptf in portfolios[date].items():
                total_long_volume = ptf.loc[ptf[POSITION] == LONG, VOLUME].sum()
                total_short_volume = ptf.loc[ptf[POSITION] == SHORT, VOLUME].sum()
            
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] = ptf[VOLUME] / total_long_volume if total_long_volume != 0 else 0
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = -ptf[VOLUME] / total_short_volume if total_short_volume != 0 else 0
            
                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
        return portfolios
    
    @staticmethod
    def get_inverse_volatility_weight(portfolios: dict) -> dict:
        """
        Adjust weights inversely proportional to the volatility of each position in the portfolio, with normalization,
        separately for long and short positions.
    
        :param portfolios: Dictionary of portfolio data.
        :return: Updated dictionary with normalized inverse volatility weights for both long and short positions.
        """
        for date in portfolios.keys():
            for name, ptf in portfolios[date].items():
                long_inverse_volatility = 1 / ptf.loc[ptf[POSITION] == LONG, VOLATILITY]
                short_inverse_volatility = 1 / ptf.loc[ptf[POSITION] == SHORT, VOLATILITY]
            
                total_long_inv_vol = long_inverse_volatility.sum()
                total_short_inv_vol = short_inverse_volatility.sum()
            
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] = long_inverse_volatility / total_long_inv_vol if total_long_inv_vol != 0 else 0
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = -short_inverse_volatility / total_short_inv_vol if total_short_inv_vol != 0 else 0
            
                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
        return portfolios
    
    @staticmethod
    def get_dollar_volume_weight(portfolios: dict) -> dict:
        """
        Adjust weights based on the dollar volume (price * volume) of each position, separately for long and short positions.
    
        :param portfolios: Dictionary of portfolio data.
        :return: Updated dictionary with weights based on dollar volume for both long and short positions.
        """
        for date in portfolios.keys():
            for name, ptf in portfolios[date].items():
                long_dollar_volume = ptf.loc[ptf[POSITION] == LONG, PX_LAST] * ptf.loc[ptf[POSITION] == LONG, VOLUME]
                short_dollar_volume = ptf.loc[ptf[POSITION] == SHORT, PX_LAST] * ptf.loc[ptf[POSITION] == SHORT, VOLUME]
            
                total_long_dollar_vol = long_dollar_volume.sum()
                total_short_dollar_vol = short_dollar_volume.sum()
            
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] = long_dollar_volume / total_long_dollar_vol if total_long_dollar_vol != 0 else 0
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = -short_dollar_volume / total_short_dollar_vol if total_short_dollar_vol != 0 else 0
            
                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
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
                sharpe_ratios = (ptf[RETURNS] - ptf[RFR]) / ptf[RETURNS].std()
                sharpe_ratios = sharpe_ratios.replace([np.inf, -np.inf, np.nan], 0)

                long_weights = sharpe_ratios[ptf[POSITION] == LONG]
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] = long_weights / long_weights.sum()
                short_weights = sharpe_ratios[ptf[POSITION] == SHORT]
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = -(abs(short_weights) / abs(short_weights).sum())

                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
        return portfolios
    
    
    @staticmethod
    def __get_dated_results(dated_portfolio: pd.DataFrame) -> float:
        """
        Calculate the aggregated weighted returns and volatility for a given portfolio on a specific date.
        
        :param dated_portfolio: DataFrame representing a single portfolio on a specific date.
        
        :return: Tuple containing summed weighted returns and summed weighted volatility.
        """
        return dated_portfolio[WEIGHTED_RETURNS].sum()
    
    def get_full_results(self, portfolios:dict) -> dict:
        """
        Aggregate results across all dates for each portfolio, computing overall returns and volatility.
        
        :param portfolios: Dictionary of portfolios, keyed by date and portfolio name.
        
        :return: Dictionary keyed by portfolio name with DataFrames containing cumulative returns and volatility data.
        """
    
        dict_returns = {}
        for date, ptf in portfolios.items():
            for key, portfolio_df in ptf.items():
                full_returns = self.__get_dated_results(portfolio_df)
                if key not in dict_returns:
                    dict_returns[key] = pd.DataFrame(columns=[DATES, RETURNS]).set_index(DATES)
                new_data = pd.DataFrame({DATES: [date], RETURNS: [full_returns]}).set_index(DATES)
                dict_returns[key] = dict_returns[key].dropna(axis=1, how='all')
                dict_returns[key] = pd.concat([dict_returns[key], new_data], ignore_index=False)
        return dict_returns

