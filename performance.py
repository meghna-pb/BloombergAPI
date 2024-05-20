import pandas as pd
import numpy as np

from optimisation import DATES, RETURNS, WEIGHT

SHARPE_RATIO = "SHARPE_RATIO"

class Performance: 
    def __init__(self, portfolios, bench):
        """
        Initialize the Performance class with portfolio data.
        
        :param portfolio: DataFrame with portfolio data, including columns ['RETURNS', 'VOLATILITY']
        """
        self.portfolios = portfolios
        self.bench = bench

    def compute_t_stat(self):
        # Initialize a dictionary to store t-stats for each portfolio
        t_stats = {}

        for portfolio_name, data in self.portfolios.items():
            # Assuming 'DATES' in portfolio and indexing benchmarks by date
            benchmark_subset = self.bench.loc[self.bench.index.isin(data.index)]

            differences = data['RETURNS'] - benchmark_subset['WEIGHTED_RETURNS']

            # Calculate mean and standard deviation of differences
            mean_diff = differences.mean()
            std_dev_diff = differences.std()
            n = differences.count()  # number of non-NA observations

            # Calculate t-statistic
            if std_dev_diff > 0 and n > 1:  # to avoid division by zero
                t_stat = mean_diff / (std_dev_diff / np.sqrt(n))
                t_stats[portfolio_name] = t_stat
            else:
                t_stats[portfolio_name] = None

        return t_stats

    def overall_performance(self) -> dict:  
        """
        Calculate the overall performance for each portfolio by computing the total compounded return from all periods.
        
        :return: A dictionary with the total compounded returns for each portfolio.
        """
        dict_results = {}
        for key, data in self.portfolios.items():
            dict_results[key] = round(((data[RETURNS] + 1).cumprod().iloc[-1] - 1), 2)
        return dict_results
    
        # dict_results = {}
        # for key, data in self.portfolios.items():
        #     log_returns = np.log1p(data[RETURNS])  
        #     total_log_return = log_returns.sum()
        #     compounded_return = np.expm1(total_log_return)  
            
        #     dict_results[key] = round(compounded_return, 2)
        # return dict_results
    
    def annualized_performance(self) -> dict:
        """
        Calculate the annualized performance for each portfolio based on the total compounded return and the number of periods.
        
        :return: A dictionary with the annualized returns for each portfolio, assuming 252 trading days per year.
        """
        dict_overall_perf = self.overall_performance()  
        dict_results = {}
        for key, overall_return in dict_overall_perf.items():
            num_periods = len(self.portfolios[key])  
            dict_results[key] = round(((1 + overall_return)**(252 / num_periods) - 1), 2)
        return dict_results
    
    def monthly_volatility(self)-> dict:   
        """
        Calculate the standard deviation of monthly returns for each portfolio.
        
        :return: A dictionary with the monthly volatility for each portfolio.
        """
        dict_results = {}
        for key, data in self.portfolios.items():
            dict_results[key] = round(data[RETURNS].std(), 2)
        return dict_results
    
    def annualized_volatility(self)-> dict:
        """
        Calculate the annualized volatility for each portfolio by scaling the monthly volatility to an annual basis using the square root of time scaling factor (sqrt(12)).
        
        :return: A dictionary with the annualized volatility for each portfolio.
        """
        dict_monthly_vol = self.monthly_volatility()  
        dict_results = {}
        for key, monthly_vol in dict_monthly_vol.items():
            dict_results[key] = round(monthly_vol*np.sqrt(12), 2)
            # sqrt(12) ?????????? 
        return dict_results
    
    def max_drawdown(self) -> dict:
        """
        Calculate the maximum drawdown for each portfolio, 
            which is the maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained.
        
        :return: A dictionary with the maximum drawdown for each portfolio.
        """
        dict_results = {}
        for key, data in self.portfolios.items():
            dict_results[key] = round((data[RETURNS].dropna()+1).cumprod().diff().min(), 2)
        return dict_results
    
    def value_at_risk(self, confidence_level=0.05):
        """
        Calculate the Value at Risk (VaR) at a specified confidence level for each portfolio. 
    
        :param confidence_level: Confidence level for the VaR calculation, default is 0.05 (95% confidence).
        :return: A dictionary with the VaR for each portfolio, negative values indicate losses.
        """
        results = {}
        for key, data in self.portfolios.items() : #self.portfolio.items():
            results[key] = round(np.percentile(data[RETURNS], 100 * (1 - confidence_level)), 2)
        return results
    
    def sharpe_ratio(self, risk_free_rate):
        """
        Calculate the Sharpe Ratio for each portfolio based on returns provided in 'dict_returns'.
    
        :param risk_free_rate: The risk-free interest rate.
        :return: A dictionary with Sharpe Ratios for each portfolio.
        """
        results = {}
        for key, data in self.portfolios.items(): # self.portfolio.items():
            results[key] = round((data[RETURNS].mean() - risk_free_rate) / data[RETURNS].std(), 2)
            # * np.sqrt(12) ? je sais jamais ou il faut le mettre 
        return results
    
    def tracking_error(self):
        """
        Calculate the tracking error against a benchmark for each portfolio. 
    
        :param dict_returns: Dictionary containing returns data for each portfolio.
        :param benchmark_returns: DataFrame or Series containing the benchmark returns.
        :return: A dictionary with tracking error values for each portfolio.
        """
        results = {}
        for portfolio_name, data in self.portfolios.items():
            benchmark_subset = self.bench.loc[self.bench.index.isin(data.index)]
            results[portfolio_name] = (data[RETURNS] - benchmark_subset['WEIGHTED_RETURNS']).std()
        return results
