import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import Union, List
import plotly.graph_objects as go

"""TEST DE PERFORMANCE (performance.py) :

- Calcul de la tracking error 
- Calcul du ratio de sharpe 
- Calcul de la Value at Risk 
- Calcul des performances 
- Graphiques des performances (+ perf cumulées) 
- Calcul de la t-stat pour tous les résultats  """

class Performance: 
    def __init__(self, portfolio, risk_free_rate=0.02):
        """
        :param bench: DataFrame with benchmark data, including columns ['ticker', 'PX_LAST']
        :param portfolio: DataFrame with portfolio data, including columns ['ticker', 'weight', 'PX_LAST']
        :param risk_free_rate: Risk-free rate, default is 2%
        """
        # self.bench = bench
        self.portfolio = portfolio
        self.risk_free_rate = risk_free_rate
        # C'est quoi le bench c'est quoi le portfolio ici ? 

    
    def tracking_error(self):
        bench_returns = self.weighted_returns(bench=True)
        portfolio_returns = self.weighted_returns()
        difference = portfolio_returns - bench_returns
        return difference.std() * np.sqrt(12)

    def sharpe_ratio(self):
        portfolio_returns = self.portfolio_returns()
        excess_returns = portfolio_returns - self.risk_free_rate / 12 # on divise par 12 parce que monthly returns --> maintenabilité du code: mettre si montlhy ou daily
        return excess_returns.mean() / excess_returns.std() * np.sqrt(12) # on divise par 12 parce que monthly returns

    def VaR(self, confidence_level=0.95):
        portfolio_returns = self.portfolio_returns()
        return portfolio_returns.quantile(1 - confidence_level)


    def table(self, returns_dict:dict, portfolios_R:Union[str, List[str]], portfolios_V:Union[str, List[str]]) :
        """
        Function to generates a table containing the mean returns for cross-portfolio combinations.

        :param returns_dict : Dictionary containing full returns data for each portfolio.
        :param portfolios_R : Name(s) of portfolio(s) related to returns.
        :param portfolios_V : Name(s) of portfolio(s) related to volumes.

        :returns : DataFrame containing mean returns for cross-portfolio combinations.
    """
        
        if portfolios_R is None or len(portfolios_R) == 0:
            print("Please, select returns portfolios")
            pass
        elif portfolios_V is None or len(portfolios_V) == 0:
            print("Please, select volume portfolios")
            pass
                
        tab = pd.DataFrame(index=portfolios_R, columns=portfolios_V)
        for r in portfolios_R:
            for v in portfolios_V:
                tab.loc[r, v] = np.mean(returns_dict[f"{r}_{v}"]["Full_Returns"])
        return tab


    def viewer(self, returns_dict: dict, portfolio_keys: Union[str, List[str]] = None):
        """
        Function to visualize the full returns over time for specific portfolio(s) or all portfolios using Plotly.
        
        :param returns_dict: Dictionary containing full returns data for each portfolio.
        :param portfolio_keys: Key(s) of the portfolio(s) for which returns will be visualized. If None, all portfolios will be plotted.
        """
        if portfolio_keys is None:
            portfolio_keys = list(returns_dict.keys())
            title = 'Full Returns Over Time for All Portfolios'
        elif isinstance(portfolio_keys, str):
            portfolio_keys = [portfolio_keys]
            title = f'Full Returns Over Time for Portfolio {portfolio_keys[0]}'
        else:
            title = 'Full Returns Over Time for Selected Portfolios'
            
        fig = go.Figure()
        for portfolio_key in portfolio_keys:
            if portfolio_key not in returns_dict:
                print(f"Portfolio key '{portfolio_key}' not found.")
                continue
            portfolio_data = returns_dict[portfolio_key]
            fig.add_trace(go.Scatter(x=portfolio_data['Date'], y=portfolio_data['Full_Returns'], mode='lines+markers', name=f'Portfolio {portfolio_key}'))

        fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Full Returns', legend_title='Portfolios')
        fig.show()


    def t_stat(self):
        portfolio_returns = self.portfolio_returns()
        return stats.ttest_1samp(portfolio_returns, 0) # à coder pour de vrai 