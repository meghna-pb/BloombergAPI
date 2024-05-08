import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from data import Data, RETURNS, VOLUME, VOLATILITY, EXPECTED_RETURNS
WEIGHT, WEIGHTED_RETURNS = "WEIGHT", "WEIGHTED_RETURNS"
POSITION, LONG, SHORT = "POSITION", "LONG", "SHORT"

class Signal:
    def __init__(self, data:Data, K:int=1, n_returns:int=5, m_volume:int=3):
        self.data = data.get_data(K=K)
        self.n = n_returns
        self.m = m_volume
        self.simple_returns_portfolios = None
        self.simple_volume_portfolios = None
        self.intersected_portfolios = None

    def create_simple_portfolios(self) -> tuple:
        dict_returns, dict_volume = {}, {}
        for date, date_data in self.data.items():    
            dated_data = date_data.dropna() # subset=[PX_LAST, VOLUME], how="all"  
            dict_returns[date], dict_volume[date] = self.__create_dated_portfolio(dated_data)
        
        self.simple_returns_portfolios = dict_returns
        self.simple_volume_portfolios = dict_volume
        return self.simple_returns_portfolios, self.simple_volume_portfolios

    def __create_dated_portfolio(self, dated_data) -> tuple:
        returns_ptf, volume_ptf = {}, {}
        sorted_by_returns = dated_data.sort_values(by=RETURNS, ascending=False)
        sorted_by_volume = dated_data.sort_values(by=VOLUME, ascending=False)

        for i in range(self.n):
            portfolio = sorted_by_returns.iloc[i * len(sorted_by_returns) // self.n:(i + 1) * len(sorted_by_returns) // self.n]
            portfolio[POSITION] = LONG
            returns_ptf[f'R{i+1}'] = portfolio
        returns_ptf[f'R{i+1}-R1'] = self.__add_longshort_portfolios(long_ptf=returns_ptf[f'R{i+1}'], short_ptf=returns_ptf[f'R1'].copy())

        for j in range(self.m):
            portfolio = sorted_by_volume.iloc[j * len(sorted_by_volume) // self.m:(j + 1) * len(sorted_by_volume) // self.m]
            portfolio[POSITION] = LONG
            volume_ptf[f'V{j+1}'] = portfolio
        volume_ptf[f'V{j+1}-V1'] = self.__add_longshort_portfolios(long_ptf=volume_ptf[f'V{j+1}'], short_ptf=volume_ptf[f'V1'].copy())

        return returns_ptf, volume_ptf
    
    def __add_longshort_portfolios(self, long_ptf:pd.DataFrame, short_ptf:pd.DataFrame) -> pd.DataFrame:
        long_ptf[POSITION] = LONG
        short_ptf[POSITION] = SHORT
        return pd.concat([long_ptf, short_ptf])
    

    def create_intersected_portfolios(self, returns_ptf: dict, volume_ptf: dict) -> dict:
        dict_intersections = {}
    
        for date in self.data.keys():
            dict_intersections[date] = {}
            try :
                for R_i, R_portfolio in returns_ptf[date].items():
                    for V_j, V_portfolio in volume_ptf[date].items():
                        if not WEIGHT in R_portfolio.columns or not WEIGHT in V_portfolio.columns:
                            raise ("Intersected portfolios requires asset weighting")
                    
                        intersection_index = R_portfolio.index.intersection(V_portfolio.index)
                        intersected_portfolio = pd.concat([R_portfolio.loc[intersection_index], R_portfolio.loc[intersection_index, :]])

                        intersected_portfolio[WEIGHT] = R_portfolio.loc[intersection_index, WEIGHT] + V_portfolio.loc[intersection_index, WEIGHT]
                        intersected_portfolio[WEIGHTED_RETURNS] = R_portfolio.loc[intersection_index, WEIGHTED_RETURNS] + V_portfolio.loc[intersection_index, WEIGHTED_RETURNS]
                        intersected_portfolio.drop(POSITION, axis=1, inplace=True)
                    
                        dict_intersections[date][f'{R_i}_{V_j}'] = intersected_portfolio
            except KeyError:
                print(date)
                continue
                    
        self.intersected_portfolios = dict_intersections
        return self.intersected_portfolios

