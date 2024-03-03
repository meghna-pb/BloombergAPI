import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

"""TEST DE PERFORMANCE (performance.py) :

- Calcul de la tracking error 
- Calcul du ratio de sharpe 
- Calcul de la Value at Risk 
- Calcul des performances 
- Graphiques des performances (+ perf cumulées) 
- Calcul de la t-stat pour tous les résultats  """

class Performance:
    def __init__(self, bench, portfolio, risk_free_rate=0.02):
        """
        :param bench: DataFrame with benchmark data, including columns ['ticker', 'PX_LAST']
        :param portfolio: DataFrame with portfolio data, including columns [ 'ticker', 'weight', 'PX_LAST']
        :param risk_free_rate: Risk-free rate, default is 2%
        """
        self.bench = bench
        self.portfolio = portfolio
        self.risk_free_rate = risk_free_rate

    def calculate_returns(self, bench=False):
        """
         calculates returns.
        """
        if bench:
            data = self.bench
        else:
            data = self.portfolio
        
        #data_agg = data.groupby(level=0).agg({'weight': 'sum'}).reset_index() # dans l'éventualité où on a 2x le meme ticker à une date (on a pas encore les poids donc cette ligne est inutile)
        # data['returns'] = data['PX_LAST'].pct_change().dropna() # monthly returns
        # weighted_returns = data_agg['returns'].multiply(data_agg.set_index(['ticker'])['weight'], axis=0)
        # final_returns = weighted_returns.groupby(level='date').sum()
            
        #version 03/03 Meghna
        returns_dict = {}
        prev_df = None
        for date, df in data.items():
            if prev_df is not None:
                merged_df = pd.merge(df, prev_df, how='inner', left_index=True, right_index=True, suffixes=('', '_prev'))
                merged_df['returns'] = (merged_df['PX_LAST'] / merged_df['PX_LAST_prev']) - 1
                merged_df = merged_df.dropna(subset=['returns'])
                returns_dict[date] = merged_df
            prev_df = df

        return returns_dict
    
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

    def perf_ptf(self):
        return (1 + self.portfolio_returns()).cumprod()

    def perf_viewer(self):
        plt.figure(figsize=(14, 7))
        plt.subplot(1, 2, 1)
        plt.plot(self.perf_ptf(), label='Portfolio Cumulative Returns')
        plt.title('Portfolio Cumulative Returns')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(self.portfolio_returns(), label='Portfolio Daily Returns')
        plt.title('Portfolio Daily Returns')
        plt.legend()

        plt.show()

    def t_stat(self):
        portfolio_returns = self.portfolio_returns()
        return stats.ttest_1samp(portfolio_returns, 0) # à coder pour de vrai 