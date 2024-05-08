import pandas as pd
import numpy as np

from signals import RETURNS, EXPECTED_RETURNS, VOLATILITY, WEIGHT, WEIGHTED_RETURNS, POSITION, LONG, SHORT, RETURNS

DATES = "DATES"


class Optimisation:
    def __init__ (self, returns_portfolios:dict, volume_portfolios:dict):
        self.returns_portfolios = returns_portfolios
        self.volume_portfolios = volume_portfolios

        
    @staticmethod
    def get_equal_weight(portfolios:dict) -> dict:
        for date in portfolios.keys():  
            for name, ptf in portfolios[date].items():
                nb_long_shares = len(ptf[ptf[POSITION] == LONG].dropna())
                nb_short_shares = len(ptf[ptf[POSITION] == SHORT].dropna())
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] =  1 / nb_long_shares if nb_long_shares != 0 else 0
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = - 1 / nb_short_shares if nb_short_shares != 0 else 0
                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
        return portfolios
    
    @staticmethod
    def get_scaling_weight(portfolios: dict) -> dict:
        for date in portfolios.keys():
            for name, ptf in portfolios[date].items():
                ptf[WEIGHT] = 1 / ptf[VOLATILITY]
                ptf.loc[ptf[POSITION] == LONG, WEIGHT] = ptf[WEIGHT]
                ptf.loc[ptf[POSITION] == SHORT, WEIGHT] = -ptf[WEIGHT]
                total_weight = ptf[WEIGHT].abs().sum()
                ptf[WEIGHT] /= total_weight
                ptf[WEIGHTED_RETURNS] = ptf[RETURNS] * ptf[WEIGHT]
        return portfolios
    
    @staticmethod
    def __get_dated_returns(dated_portfolio: pd.DataFrame) -> float:
        return dated_portfolio[WEIGHTED_RETURNS].sum()
    
    def get_full_returns(self, portfolios:dict) -> dict:
        dict_returns = {}
        for date, ptf in portfolios.items():
            for key, portfolio_df in ptf.items():
                full_returns = self.__get_dated_returns(portfolio_df)
                if key not in dict_returns:
                    dict_returns[key] = pd.DataFrame(columns=[DATES, RETURNS])
                new_data = pd.DataFrame({DATES: [date], RETURNS: [full_returns]})
                dict_returns[key] = dict_returns[key].dropna(axis=1, how='all')
                dict_returns[key] = pd.concat([dict_returns[key], new_data], ignore_index=True)
        return dict_returns


    def get_weighted_returns(self):
        results_returns, results_volume = {}, {}

        weighting_methods = {
            'Equal Weight': self.get_equal_weight,
            'Scaling Weight': self.get_scaling_weight,
        }

        for method_name, method in weighting_methods.items():
            weighted_returns = method(self.returns_portfolios.copy())  
            weighted_volume = method(self.volume_portfolios.copy()) 

            total_returns = self.get_full_returns(weighted_returns)
            total_volume = self.get_full_returns(weighted_volume)

            sum_returns = sum(df[RETURNS].sum() for df in total_returns.values())
            sum_volume = sum(df[RETURNS].sum() for df in total_volume.values())
            
            results_returns[method_name] = (sum_returns, total_returns)
            results_volume[method_name] = (sum_volume, total_volume)

        best_method_returns = max(results_returns, key=lambda x: results_returns[x][0])
        best_method_volume = max(results_volume, key=lambda x: results_volume[x][0])

        print(f"The best method is for R: {best_method_returns}")
        print(f"The best method is for V: {best_method_volume}")
        return results_returns[best_method_returns][1], results_volume[best_method_volume][1]

        
        
