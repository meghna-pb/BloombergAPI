import pandas as pd
from performance import Performance

DATE = "date" # maintenabilité du code + on ne sait pas comment la colonne s'appelle dans bloom
VOLUME = "PX_VOLUME"

class Signal:
    def __init__(self, bench, portfolio, exclu, risk_free_rate=0.02):
        """
        Initializes the Signal object.

        :param bench: DataFrame with benchmark data.
        :param portfolio: DataFrame with portfolio data including 'ticker', 'weight', 'PX_LAST', and other necessary columns.
        :param exclu: DataFrame with the FD167 & DY992 fields for exclusion criteria.
        :param risk_free_rate: Risk-free rate, default is 2%.
        """
        # Preprocess portfolio to mark eligible companies
        self.exclu = exclu
        portfolio['eligible'] = ~portfolio['ticker'].isin(exclu['FD167']) & ~portfolio['ticker'].isin(exclu['DY992']) #for open ended funds and ADR
        self.performance = Performance(bench, portfolio, risk_free_rate)


    def create_portfolios(self, n_returns, m_volume):
        """
        Creates n return portfolios and m volume portfolios for each date 
        :param n_returns: Number of return portfolios to create for each date.
        :param m_volume: Number of volume portfolios to create for each date.
        :return: A dictionary containing the return and volume portfolios for each date.
        """
        portfolios = {'returns': {}, VOLUME: {}}

        # Filter eligible data
        eligible_data = self.performance.portfolio[self.performance.portfolio['eligible']]
        eligible_data= self.performance.calculate_returns()

        # For each date, create the portfolios
        for date in eligible_data[DATE].unique():
            date_data = eligible_data[eligible_data[DATE] == date]
            
            # Sort by returns and volume
            sorted_by_returns = date_data.sort_values(by='returns', ascending=False)
            sorted_by_volume = date_data.sort_values(by=VOLUME, ascending=False)

            # Create return portfolios for this date
            portfolios['returns'][date] = [sorted_by_returns.iloc[i::n_returns] for i in range(min(n_returns, len(sorted_by_returns)))]
            
            # Create volume portfolios for this date
            portfolios[VOLUME][date] = [sorted_by_volume.iloc[i::m_volume] for i in range(min(m_volume, len(sorted_by_volume)))]

        return portfolios