import pandas as pd
from typing import Union, List
import plotly.graph_objects as go

from performance import Performance, RETURNS
# RETURNS = "WEIGHTED_RETURNS"

class Charts(Performance):
    def __init__(self, portfolios, bench):
        """
        Initialize the Charts class which inherits from the Performance class.
        
        :param portfolio: DataFrame with portfolio data, including columns ['RETURNS', 'VOLATILITY']
        """
        super().__init__(portfolios, bench)
        
    def viewer(self, portfolio_keys: Union[str, List[str]] = None):
        """
        Function to visualize the full returns over time for specific portfolio(s) or all portfolios using Plotly.
        
        :param portfolio_keys: Key(s) of the portfolio(s) for which returns will be visualized. If None, all portfolios will be plotted.
        """
        if portfolio_keys is None:
            portfolio_keys = list(self.portfolios.keys())
            title = 'Full Returns Over Time for All Portfolios'
        elif isinstance(portfolio_keys, str):
            portfolio_keys = [portfolio_keys]
            title = f'Full Returns Over Time for Portfolio {portfolio_keys[0]}'
        else:
            title = 'Full Returns Over Time for Selected Portfolios'
            
        fig = go.Figure()
        for portfolio_key in portfolio_keys:
            if portfolio_key not in self.portfolios:
                print(f"Portfolio key '{portfolio_key}' not found.")
                continue
            portfolio_data = self.portfolios[portfolio_key]
            fig.add_trace(go.Scatter(x=portfolio_data.index, y=portfolio_data[RETURNS], mode='lines+markers', name=f'Portfolio {portfolio_key}'))

        fig.update_layout(title=title, xaxis_title='Dates', yaxis_title=RETURNS, legend_title='Portfolios')
        fig.show()  
        
    def cumulative_viewer(self, portfolio_keys: Union[str, List[str]] = None):
        """
        Function to visualize the cumulative returns over time for specific portfolio(s) or all portfolios using Plotly.
        
        :param portfolio_keys: Key(s) of the portfolio(s) for which returns will be visualized. If None, all portfolios will be plotted.
        """
        if portfolio_keys is None:
            portfolio_keys = list(self.portfolios.keys())
            title = 'Cumulative Returns Over Time for All Portfolios'
        elif isinstance(portfolio_keys, str):
            portfolio_keys = [portfolio_keys]
            title = f'Cumulative Returns Over Time for Portfolio {portfolio_keys[0]}'
        else:
            title = 'Cumulative Returns Over Time for Selected Portfolios'
        
        fig = go.Figure()
        for portfolio_key in portfolio_keys:
            if portfolio_key not in self.portfolios:
                print(f"Portfolio key '{portfolio_key}' not found.")
                continue
            portfolio_data = self.portfolios[portfolio_key]
            cumulative_returns = (1 + portfolio_data[RETURNS]).cumprod() - 1
            fig.add_trace(go.Scatter(x=portfolio_data.index, y=cumulative_returns, mode='lines+markers', name=f'Portfolio {portfolio_key}'))
        
        fig.update_layout(title=title, xaxis_title='Dates', yaxis_title='Cumulative Returns', legend_title='Portfolios')
        fig.show()

    def get_table(self, portfolio_keys: Union[str, List[str]] = None):
        """
        Gathers all performance metrics and displays them in a single DataFrame.
    
        :param portfolio_keys: Optional list of portfolio keys to filter the results.
        :return: DataFrame containing all performance metrics for specified portfolios.
        """
        
        # Create a DataFrame from the collected metrics
        results_df = pd.DataFrame({
            "Overall Performance": self.overall_performance(),
            "Annualized Performance": self.annualized_performance(),
            "Monthly Volatility": self.monthly_volatility(),
            "Annualized Volatility": self.annualized_volatility(),
            "Maximum Drawdown": self.max_drawdown(),
            "Sharpe Ratio": self.sharpe_ratio(0.2), 
            "Tracking Error":self.tracking_error(), 
            "t-stat":self.compute_t_stat()
        })
        
        # If keys are provided, filter the DataFrame to include only those portfolios
        if portfolio_keys is not None:
            results_df = results_df[results_df.index.isin(portfolio_keys)]
        
        return results_df
    
    def get_figures(self, column_name:str, portfolio_keys: Union[str, List[str]] = None):
        """
    Plot a histogram using Plotly for the specified column in the DataFrame.

    :param data: DataFrame containing the data.
    :param column_name: Name of the column to plot.
    """
        # Create a DataFrame from the collected metrics
        results_df = self.get_table(portfolio_keys)
        if column_name in results_df.columns:
            # Create the histogram
            fig = go.Figure(data=[go.Histogram(x=results_df[column_name])])
            
            # Update layout
            fig.update_layout(
                title=f'Histogram of {column_name}',
                xaxis_title=column_name,
                xaxis=dict( tickmode='auto',  # Could be 'auto' or 'linear' or 'array'
                            tickformat=',',),  # Use ',' as a thousand separator to show full numbers.
                yaxis_title='Frequency',
                # bargap=0.2, 
                template='plotly_white' 
            )
            
            fig.show()
        else:
            print(f"Column '{column_name}' not found in the DataFrame.")


    
    