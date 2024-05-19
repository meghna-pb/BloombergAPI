
import pandas as pd 
import numpy as np
from BLP import BLP
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt 


class Figures():
    """
    This class enable to compute risk metrics.
    """

    def daily_historical_var(self, df_ptf_returns: pd.DataFrame,
                             i_alpha: int = 5) -> float:
        return round(np.percentile(df_ptf_returns.dropna(), i_alpha),3)

    def sharpe_ratio(self, df_ptf_returns: pd.DataFrame, s_risk_free:
                     str = 'GDBR10 Index') -> float:

        # 1. Get risk free rate for each date
        blp = BLP()
        field = "PX_LAST"
        dict_rf = blp.bdh(l_security=s_risk_free, l_fields=field,
                          dt_startdate=df_ptf_returns.index.tolist()[0],
                          dt_enddate=df_ptf_returns.index.tolist()[-1])
        blp.closeSession()
        df_rf = dict_rf.get(field)
        df_rf = df_rf.set_index(pd.to_datetime(df_rf.index))
        # Convert annual risk free returns to daily risk free returns
        df_rf = ((df_rf + 1)**(1/252))-1

        # 2. Merge the 2 series (risk free rate & portoflio returns) on the_
        # index so that dates match.

        df_ptf_returns.columns = ['Ptf_returns']
        df_merged = pd.merge(df_ptf_returns, df_rf.rename(
            columns={s_risk_free: 'Rf'}), left_index=True,
            right_index=True, how='left')

        # 3. Compute excess returns
        df_excess_returns = df_merged.Ptf_returns - df_merged.Rf
        f_avg_excess_returns = df_excess_returns.mean()

        # 4. Compute standard deviation
        f_std_excess_returns = df_excess_returns.std()
        return round(f_avg_excess_returns / f_std_excess_returns, 3)






    def analyse_portfolio(self,  df_ptf_returns: pd.DataFrame, i_alpha:
                          int = 5, s_risk_free: str = 'GDBR10 Index'
                          ) -> pd.DataFrame:
        df_results = pd.DataFrame(columns=['overall_perf', 'annualized_perf',
                                           'daily_vol', 'monthly_vol',
                                           'annualized_vol', 'max_drawdown',
                                           'daily_historical_var',
                                           'sharpe_ratio'])
        df_results.loc[0, 'overall_perf'] = (
            f'{round(self.overall_perf(df_ptf_returns)*100,2)}%')
        df_results.loc[0, 'annualized_perf'] = (
            f'{round(self.annualized_perf(df_ptf_returns)*100,2)}%')
        df_results.loc[0, 'daily_vol'] = (
            f'{round(self.daily_vol(df_ptf_returns)*100,2)}%')
        df_results.loc[0, 'monthly_vol'] = (
            f'{round(self.monthly_vol(df_ptf_returns)*100,2)}%')
        df_results.loc[0, 'annualized_vol'] = (
            f'{round(self.annualized_vol(df_ptf_returns)*100,2)}%')
        df_results.loc[0, 'max_drawdown'] = (
            f'{round(self.max_drawdown(df_ptf_returns)*100,2)}%')
        df_results.loc[0, 'daily_historical_var'] = self.daily_historical_var(
            df_ptf_returns, i_alpha)
        df_results.loc[0, 'sharpe_ratio'] = self.sharpe_ratio(df_ptf_returns,
                                                          s_risk_free)

        df_results = df_results.set_index(pd.Index([
            df_ptf_returns.index.tolist()[-1]])).transpose()
        
        df_results = df_results.reset_index(drop=False)
        df_results = df_results.rename(columns={'index': 'Figures'})

        fig, ax = plt.subplots(1, 1)
        ax.axis('tight')
        ax.axis('off')
        ax.table(cellText=df_results.values, colLabels=df_results.columns,
                 loc='center', colColours =['xkcd:sky blue'] * 2)
    
        plt.savefig('Figures.png', dpi=300, bbox_inches='tight')
        plt.show()
        return df_results
