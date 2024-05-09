import pandas as pd
import numpy as np
from typing import Union, List
import plotly.graph_objects as go

from optimisation import DATES, RETURNS

class Performance: 
    def __init__(self, portfolio):
        """
        Initialize the Performance class with portfolio data.
        
        :param portfolio: DataFrame with portfolio data, including columns ['ticker', 'weight', 'PX_LAST']
        """
        self.portfolio = portfolio


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
            fig.add_trace(go.Scatter(x=portfolio_data[DATES], y=portfolio_data[RETURNS], mode='lines+markers', name=f'Portfolio {portfolio_key}'))

        fig.update_layout(title=title, xaxis_title=DATES, yaxis_title=RETURNS, legend_title='Portfolios')
        fig.show()
        
    def table(self, dict_returns:dict, ptf_R:Union[str, List[str]], ptf_V:Union[str, List[str]]) :     
        """
        Generate a table comparing returns across specified portfolios.
        
        :param dict_returns: Dictionary of returns data keyed by portfolio and variable (e.g., 'R_V').
        :param ptf_R: List or string of portfolio keys to include as rows in the table.
        :param ptf_V: List or string of portfolio keys to include as columns in the table.
        """
        if ptf_R is None or len(ptf_R) == 0:
            raise ("Select returns portfolios")
        elif ptf_V is None or len(ptf_V) == 0:
            raise ("Select volume portfolios")
                
        tab = pd.DataFrame(index=ptf_R, columns=ptf_V)
        for r in ptf_R:
            for v in ptf_V:
                tab.loc[r, v] = np.mean(dict_returns[f"{r}_{v}"][RETURNS])
        return tab