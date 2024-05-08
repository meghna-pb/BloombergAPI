import pandas as pd
from performance import Performance
from data import Data, VOLUME,PX_LAST, RETURNS

pd.options.mode.chained_assignment = None

# Déclaration des variables
POSITION = "POSITION"
SHORT, LONG = "SHORT", "LONG"

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
        sorted_by_returns = data.sort_values(by=RETURNS, ascending=True) ## False 
        sorted_by_volume = data.sort_values(by=VOLUME, ascending=True) ## False 

        # Create return portfolios for the given date 
        for i in range(min(n_returns, len(sorted_by_returns))):
            start_idx = i * len(sorted_by_returns) // min(n_returns, len(sorted_by_returns))
            end_idx = (i + 1) * len(sorted_by_returns) // min(n_returns, len(sorted_by_returns))
            returns_ptf[f'R{i+1}'] = sorted_by_returns.iloc[start_idx:end_idx]
            returns_ptf[f'R{i+1}'].loc[:, POSITION] = LONG
        
        # R_n - R_1 (long/short): 
        returns_ptf[f'R{n_returns}-R1'] = self.create_long_short_portfolio(returns_ptf[f'R{n_returns}'], returns_ptf['R1'])

        # Create volume portfolios for the given date 
        for i in range(min(m_volume, len(sorted_by_volume))):
            start_idx = i * len(sorted_by_volume) // min(m_volume, len(sorted_by_volume))
            end_idx = (i + 1) * len(sorted_by_volume) // min(m_volume, len(sorted_by_volume))
            volume_ptf[f'V{i+1}'] = sorted_by_volume.iloc[start_idx:end_idx]
            volume_ptf[f'V{i+1}'].loc[:, POSITION] = LONG
            
        # V_m - V_1 (long/short): 
        volume_ptf[f'V{m_volume}-V1'] = self.create_long_short_portfolio(volume_ptf[f'V{m_volume}'], volume_ptf['V1'])

        return returns_ptf, volume_ptf


    def create_long_short_portfolio(self, long_ptf, short_ptf) : 
        """
            Create Long/Short portfolio 
        """
        # long_ptf = long_ptf.copy()
        # short_ptf = short_ptf.copy()
        long_ptf.loc[:, POSITION] = LONG
        short_ptf.loc[:, POSITION] = SHORT
        return pd.concat([long_ptf, short_ptf])


    def create_intersections(self, n_returns, m_volume):
        """
            Get intersections of return and volume portfolios for each date.
        """

        for date, date_data in self.data.items():    
            date_data = date_data.dropna(subset=[PX_LAST, VOLUME], how="all")     
            self.dict_portfolios[date] = {}
            
            self.dict_returns[date], self.dict_volume[date] = self.create_portfolios(date_data, n_returns, m_volume)

            for R_i, R_portfolio in self.dict_returns[date].items():
                for V_j, V_portfolio in self.dict_volume[date].items():                    
                    intersection_index = R_portfolio.index.intersection(V_portfolio.index)
                    long_short_doublon = [share for share in intersection_index if R_portfolio.loc[share, POSITION] != V_portfolio.loc[share, POSITION]]
                    ###### PROBLEME 
                    intersection_portfolio = R_portfolio.loc[intersection_index]
                    intersection_portfolio = pd.concat([intersection_portfolio, R_portfolio.loc[long_short_doublon, :]])
                    self.dict_portfolios[date][f'{R_i}_{V_j}'] = intersection_portfolio

        return self.dict_portfolios, date