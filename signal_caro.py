import pandas as pd
from performance import Performance

class Signal:
    def __init__(self, PX_LAST, PX_VOLUME, risk_free_rate=0.02):
        """
        Initializes the Signal object.

        :param risk_free_rate: Risk-free rate, default is 2%.        
        ++ :param PX_LAST: DataFrame with full PX_LAST data.
        ++ :param PX_VOLUME: DataFrame with full PX_LAST data.
        """
        
        self.px_last = PX_LAST
        self.px_volume = PX_VOLUME
        self.risk_free_rate = risk_free_rate

    def calculate_returns(self): 
        """
         calculates returns.
        """
        return self.px_last.apply(lambda colonne: colonne.pct_change().dropna())

    def filter_and_sort(self, data:pd.DataFrame, date):
        
        # STEP 1 : filtre des données sur une date (une seule ligne)
        # Bon clairement un problème sur ce filtre que j'ai pas encore réussis à résoudre (le résultat est toujours None)
        # J'ai vu que t'avais trouver un tips donc ca devrait être good avec ta technique 
        
        # filtered_data = data.loc .... 
        
        # STEP 2 : classement (volume ou rendement)
        
        # return filtered_data.sort_values()
        pass 


    def create_portfolios(self, date, n_returns, m_volume):
        returns = self.calculate_returns()
        
        sorted_returns = self.filter_and_sort(returns, date)
        sorted_volume = self.filter_and_sort(self.px_volume, date)
        
        # Ensuite on garde que les n / m premiers 
        # Ce qui nous interesse ici c'est surtout les tickers, on peut en faire une liste
        # Et après on envoie cette liste + full data à la classe performance 
        # et on en déduit les poids attribués à chacun des tickers de la liste 
        # hop on a des portefeuilles optimisés? 
