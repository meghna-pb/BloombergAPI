import pandas as pd
import numpy as np

from signals import DATES, RETURNS, WEIGHT

SHARPE_RATIO = "SHARPE_RATIO"

class Performance: 
    """This class provides methods to calculate various performance metrics for the given portfolios, including Sharpe Ratio, Value at Risk, and tracking error relative to a specified benchmark. """
    
    def __init__(self, portfolios:dict, bench:pd.DataFrame, risk_free_rate:float=0.02, confidence_level:float=0.05):
        """
        Initialize the Performance class with portfolio data and additional parameters for performance evaluation.
        
        :param portfolios: Dictionary containing portfolio data. Each key should be a portfolio name, and each value should be a DataFrame with at least the columns ['RETURNS', 'VOLATILITY'].
        :param bench: DataFrame containing benchmark data. This data is used for calculating metrics like tracking error. The DataFrame should have at least a column 'RETURNS' that corresponds to the benchmark returns.
        :param risk_free_rate: The risk-free rate to be used in financial calculations such as the Sharpe Ratio. Default is 0.2.
        :param confidence_level: The confidence level for calculating the Value at Risk (VaR). The default value is 0.05, which corresponds to 95% confidence.
        """
        self.portfolios = portfolios
        self.bench = bench
        self.risk_free_rate = risk_free_rate
        self.confidence_level = confidence_level

    def compute_t_stat(self):
        """
        Calculate the t-statistic for each portfolio compared to the benchmark to determine statistical significance
        of the differences in their returns.

        :return: A dictionary with portfolio names as keys and their respective t-statistics as values. If the
        calculation cannot be performed (e.g., due to zero standard deviation or insufficient data points), the value
        will be None for that portfolio.
        """
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
    
    def value_at_risk(self):
        """
        Calculate the Value at Risk (VaR) at a specified confidence level for each portfolio. 
    
        :param confidence_level: Confidence level for the VaR calculation, default is 0.05 (95% confidence).
        :return: A dictionary with the VaR for each portfolio, negative values indicate losses.
        """
        results = {}
        for key, data in self.portfolios.items() : 
            results[key] = round(np.percentile(data[RETURNS], 100 * (1 - self.confidence_level)), 2)
        return results
    
    def sharpe_ratio(self):
        """
        Calculate the Sharpe Ratio for each portfolio based on returns provided in 'dict_returns'.
    
        :param risk_free_rate: The risk-free interest rate.
        :return: A dictionary with Sharpe Ratios for each portfolio.
        """
        results = {}
        for key, data in self.portfolios.items(): 
            results[key] = round((data[RETURNS].mean() - self.risk_free_rate) / data[RETURNS].std(), 2)
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
