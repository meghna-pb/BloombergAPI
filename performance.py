import pandas as pd
import numpy as np
from typing import Union, List
import plotly.graph_objects as go
from data import EXPECTED_RETURNS
from optimisation import DATES, RETURNS, WEIGHT

SHARPE_RATIO = "SHARPE_RATIO"


class Performance: 
    def __init__(self, portfolio):
        """
        Initialize the Performance class with portfolio data.
        
        :param portfolio: DataFrame with portfolio data, including columns ['ticker', 'weight', 'PX_LAST']
        """
        self.portfolio = portfolio

    def viewer(self, dict_returns: dict, portfolio_keys: Union[str, List[str]] = None):
        """
        Function to visualize the full returns over time for specific portfolio(s) or all portfolios using Plotly.
        
        :param returns_dict: Dictionary containing full returns data for each portfolio.
        :param portfolio_keys: Key(s) of the portfolio(s) for which returns will be visualized. If None, all portfolios will be plotted.
        """
        if portfolio_keys is None:
            portfolio_keys = list(dict_returns.keys())
            title = 'Full Returns Over Time for All Portfolios'
        elif isinstance(portfolio_keys, str):
            portfolio_keys = [portfolio_keys]
            title = f'Full Returns Over Time for Portfolio {portfolio_keys[0]}'
        else:
            title = 'Full Returns Over Time for Selected Portfolios'
            
        fig = go.Figure()
        for portfolio_key in portfolio_keys:
            if portfolio_key not in dict_returns:
                print(f"Portfolio key '{portfolio_key}' not found.")
                continue
            portfolio_data = dict_returns[portfolio_key]
            fig.add_trace(go.Scatter(x=portfolio_data[DATES], y=portfolio_data[RETURNS], mode='lines+markers', name=f'Portfolio {portfolio_key}'))

        fig.update_layout(title=title, xaxis_title=DATES, yaxis_title=RETURNS, legend_title='Portfolios')
        fig.show()
        
    def cumulative_viewer(self, dict_returns: dict, portfolio_keys: Union[str, List[str]] = None):
        """
        Function to visualize the cumulative returns over time for specific portfolio(s) or all portfolios using Plotly.
        
        :param returns_dict: Dictionary containing full returns data for each portfolio.
        :param portfolio_keys: Key(s) of the portfolio(s) for which returns will be visualized. If None, all portfolios will be plotted.
        """
        if portfolio_keys is None:
            portfolio_keys = list(dict_returns.keys())
            title = 'Cumulative Returns Over Time for All Portfolios'
        elif isinstance(portfolio_keys, str):
            portfolio_keys = [portfolio_keys]
            title = f'Cumulative Returns Over Time for Portfolio {portfolio_keys[0]}'
        else:
            title = 'Cumulative Returns Over Time for Selected Portfolios'
        
        fig = go.Figure()
        for portfolio_key in portfolio_keys:
            if portfolio_key not in dict_returns:
                print(f"Portfolio key '{portfolio_key}' not found.")
                continue
            portfolio_data = dict_returns[portfolio_key]
            cumulative_returns = (1 + portfolio_data[RETURNS]).cumprod() - 1
            fig.add_trace(go.Scatter(x=portfolio_data[DATES], y=cumulative_returns, mode='lines+markers', name=f'Portfolio {portfolio_key}'))
        
        fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Cumulative Returns', legend_title='Portfolios')
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
    
    
    def sharpe_ratio(self, dict_returns:dict, risk_free_rate):
        """
        Calculate the Sharpe Ratio for each portfolio based on returns provided in 'dict_returns'.
    
        :param dict_returns: Dictionary containing returns data for each portfolio.
        :param risk_free_rate: The risk-free interest rate.
        :return: A dictionary with Sharpe Ratios for each portfolio.
        """
        results = {}
        for key, data in dict_returns.items(): # self.portfolio.items():
            results[key] = round((data[RETURNS].mean() - risk_free_rate) / data[RETURNS].std(), 2)
            # * np.sqrt(12) ? je sais jamais ou il faut le mettre 
        return results
    
    def value_at_risk(self, dict_returns:dict, confidence_level=0.05):
        """
        Calculate the Value at Risk (VaR) at a specified confidence level for each portfolio. 
    
        :param dict_returns: Dictionary containing returns data for each portfolio.
        :param confidence_level: Confidence level for the VaR calculation, default is 0.05 (95% confidence).
        :return: A dictionary with the VaR for each portfolio, negative values indicate losses.
        """
        results = {}
        for key, data in dict_returns.items() : #self.portfolio.items():
            results[key] = round(np.percentile(data[RETURNS], 100 * (1 - confidence_level)), 2)
        return results
    
    def tracking_error(self, dict_returns:dict, benchmark_returns):
        """
        Calculate the tracking error against a benchmark for each portfolio. 
    
        :param dict_returns: Dictionary containing returns data for each portfolio.
        :param benchmark_returns: DataFrame or Series containing the benchmark returns.
        :return: A dictionary with tracking error values for each portfolio.
        """
        results = {}
        for key, data in dict_returns.items():
            results[key] = (data[RETURNS] - benchmark_returns[RETURNS]).std()
        return results
        #### AI BESOIN D'UN BENCHMARK POUR TESTER 
    
    
    def sharpe_ratio_meghna (self, risk_free_rate):
        sharpe_ptf = {}

        unique_portfolio_names = set()
        for date in self.portfolio.keys():
            unique_portfolio_names.update(self.portfolio[date].keys())

        for name in unique_portfolio_names:
            all_excess_returns = []  
            for date in self.portfolio.keys():  
                ptf = self.portfolio[date].get(name)
                if ptf is not None and not ptf.empty:
                    excess_returns = (ptf[EXPECTED_RETURNS] * ptf[WEIGHT]) - risk_free_rate / 12
                    all_excess_returns.extend(excess_returns.tolist())

            all_excess_returns = np.array(all_excess_returns)
            sharpe_ptf[name] = np.mean(all_excess_returns) / np.std(all_excess_returns) * np.sqrt(12)
        return sharpe_ptf
    
    def VaR_meghna(self, confidence_level=0.95):
        VaR_dict = {}
        unique_portfolio_names = set()
        for date in self.portfolio.keys():
            unique_portfolio_names.update(self.portfolio[date].keys())
        for name in unique_portfolio_names:
            all_returns = []
            for date in self.portfolio.keys():
                ptf = self.portfolio[date].get(name)
                if ptf is not None and not ptf.empty:
                    returns = ptf[EXPECTED_RETURNS] * ptf[WEIGHT]
                    all_returns.extend(returns.tolist())
            all_returns = np.array(all_returns)
            if len(all_returns) > 0:
                VaR_dict[name] = -np.percentile(all_returns, confidence_level * 100)
            else:
                VaR_dict[name] = None

        return VaR_dict