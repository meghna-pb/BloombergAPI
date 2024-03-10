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
            # Pb 1 : "range(min(n_returns, len(sorted_by_returns)))" -> n_returns c'est le nombre de ptf pas de tickers dans un ptf non ?? 
            # Pb 2 : ".iloc[i::n_returns]" -> toujours la même compo 
            
            # Create volume portfolios for this date
            self.portfolios[date][VOLUME] = [sorted_by_volume.iloc[i::m_volume] for i in range(min(m_volume, len(sorted_by_volume)))]

        return self.portfolios, date # J'ai rajouté date juste pour pouvoir tester :) 
    

        """
        Ok je comprends rien : 
        
        1) n_returns et m_volume c'est le nombre de portefeuilles que l'on veut non ? 
        Dans le code la ca correspond à ca, mais aussi au nombre de tickers qu'on veut mettre dedans ? 
        
        2) Si on demande 3 ptf par exemple, les 3 auront la même compo, il faut plutot prendre les suivants et ainsi de suite
        
        3) Il y a une couille sur les colonnes allouée à chaque ptf : 
        Par ex si on demande 3 ptf, le 1er aura que la colonne PX_Last, le 2ème que PX_Volume et le 3ème que RETURNS 
        On veut les 3 colonnes pour chaque ? 
        
        4) A mon avis il y a vraiment beaucoup trop de poupée russes, des dataframe dans des dict dans des dict dans des dict ... 
        J'ai essayer de reflechir à comment simplifier mais vraiment je comprends pas ta logique et je veux pas niquer tout ce que t'as fait 
        
        """
