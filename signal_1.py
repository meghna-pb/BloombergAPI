import pandas as pd
from performance import Performance
from data import Data

DATE = "date" # on s'en sert jamais 
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
        self.dict_returns = {}
        self.dict_volume = {}
        self.dict_portfolios = {}
        

    def create_portfolios(self, data, n_returns:int, m_volume:int):
        """
        Creates n return portfolios and m volume portfolios for a given date 
        :param data: DataFrame with data filtered for one date
        :param n_returns: Number of return portfolios to create for each date.
        :param m_volume: Number of volume portfolios to create for each date.
        :return: A dictionary containing the return and volume portfolios for each date.
        """  
        returns_ptf, volume_ptf = {}, {}
        sorted_by_returns = data.sort_values(by='RETURNS', ascending=False) 
        sorted_by_volume = data.sort_values(by=VOLUME, ascending=False)    

        # Create return portfolios for the given date 
        for i in range(min(n_returns, len(sorted_by_returns))):
            start_idx = i * len(sorted_by_returns) // min(n_returns, len(sorted_by_returns))
            end_idx = (i + 1) * len(sorted_by_returns) // min(n_returns, len(sorted_by_returns))
            returns_ptf[f'R{i+1}'] = sorted_by_returns.iloc[start_idx:end_idx]

        # Create volume portfolios for the given date 
        for i in range(min(m_volume, len(sorted_by_volume))):
            start_idx = i * len(sorted_by_volume) // min(m_volume, len(sorted_by_volume))
            end_idx = (i + 1) * len(sorted_by_volume) // min(m_volume, len(sorted_by_volume))
            volume_ptf[f'V{i+1}'] = sorted_by_volume.iloc[start_idx:end_idx]

        return returns_ptf, volume_ptf


    def create_intersections(self, n_returns, m_volume):
        """
            Get intersections of return and volume portfolios for each date.
        """
        
        for date, date_data in self.data.items():    
            date_data = date_data.dropna(subset=['PX_LAST', VOLUME], how="all")     
            self.dict_portfolios[date] = {}
            
            self.dict_returns[date], self.dict_volume[date] = self.create_portfolios(date_data, n_returns, m_volume)

            for R_i, R_portfolio in self.dict_returns[date].items():
                for V_j, V_portfolio in self.dict_volume[date].items():                    
                    intersection_index = R_portfolio.index.intersection(V_portfolio.index)
                    intersection_portfolio = R_portfolio.loc[intersection_index]
                    self.dict_portfolios[date][f'{R_i}_{V_j}'] = intersection_portfolio

        return self.dict_portfolios, date

        
        """
            PETIT RESUME DES MODIFS : 
            
            1) Une nouvelle classe create_portfolios : même principe mais que pour une seule date 
            (je voulais éviter une double boucle for inutile dans le process)
            
            2) Deux nouvelles variables : dict_returns et dict_volume 
            -> Pour l'intesection c'est plus facile de les séparer 
            -> self.portfolios contient maintenant les portfeuilles après intersections
            
            3) Nouvelle fonction create_intesections : remplis le dict.portfolios
            TOUT les ptf sont construits (je sais je me contredit toute seule), à voir si ca prend vraiment plus de temps ou pas
        """