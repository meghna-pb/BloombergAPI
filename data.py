import pandas as pd

VOLUME, PX_LAST, RETURNS, VOLATILITY, RFR, WEIGHT, WEIGHTED_RETURNS = "PX_VOLUME", "PX_LAST", "RETURNS", "VOLATILITY", "RFR", "WEIGHT", "WEIGHTED_RETURNS"
class Data:
    def __init__(self, path="", J=3, risk_free_rate:float=0.2) -> None:
        """
        Initialize the Data class with the option to load data from a specified path or use predefined Bloomberg data.
        
        :param path: Path to the Excel files containing the data. If empty, uses predefined Bloomberg data.
        :param J: Number of periods used for calculating rolling statistics such as volatility and expected returns.
        :param risk_free_rate: The risk-free rate used in financial calculations.
        """
        
        self.J = J  
        self.risk_free_rate = risk_free_rate
        
        if path == "":
            from bloomberg import df_compo, dict_data
            self.df_compo = df_compo
            self.df_px_last = dict_data[PX_LAST].sort_index()
            self.df_px_volume = dict_data[VOLUME].sort_index()
        else:
            self.df_compo = pd.read_excel(path+'/Bloomberg_Compo.xlsx', sheet_name="Compo")
            self.df_px_last = pd.read_excel(path+'/Bloomberg_Data.xlsx', sheet_name='PX LAST', index_col=0)
            self.df_px_volume = pd.read_excel(path+'/Bloomberg_Data.xlsx', sheet_name='PX VOLUME', index_col=0)
        
        self.df_px_last = self.__treat_df(self.df_px_last, format='%Y%m%d')
        self.df_px_volume = self.__treat_df(self.df_px_volume, format='%Y%m%d')
        self.df_compo.columns = pd.to_datetime(self.df_compo.columns, format='%Y%m%d')
        self.df_returns = self.__calculate_returns()
        self.df_volatility = self.__calculate_volatility()
        
        
        
    def __treat_df(self, df, format) -> pd.DataFrame:
        """
        Cleans DataFrame columns, including stripping of extra characters and standardizing date formats.
        
        :param df: DataFrame to be treated.
        :param format: String format to parse the index as dates.
        """
        df.columns = df.columns.str.replace(" Equity", "")
        df.index = pd.to_datetime(df.index, format=format)
        return df.sort_index()

    def __calculate_returns(self) -> pd.DataFrame:
        """
        Calculates the percentage change in PX_LAST to derive returns, applied on a forward-filled DataFrame.
        """
        return self.df_px_last.apply(lambda colonne: colonne.ffill().pct_change(fill_method=None).dropna())
    
    def __calculate_volatility(self) -> pd.DataFrame:
        """
        Calculates rolling volatility over the specified window J and handles any resulting NA values.
        """
        df_volatility = self.df_returns.rolling(window=self.J).std()
        df_volatility.replace(0, pd.NA, inplace=True)
        df_volatility = df_volatility.fillna(method='ffill').fillna(method='bfill')
        return df_volatility

    def get_data(self, K:int=1) -> dict:
        """
        Aggregates and aligns all financial data by rebalancing date intervals, tailored for portfolio construction.
        
        :param K: Frequency of rebalance in months.
        """
        data = {}
        valid_index = self.df_px_last.index[self.J]  # +1
        rebalance_dates = pd.date_range(valid_index, self.df_px_last.index[-1], freq=f'{K}ME')

        for date in rebalance_dates :
            if date in self.df_px_last.index:
                nearest_date = min(pd.to_datetime(self.df_compo.columns), key=lambda x: abs(x - pd.to_datetime(date)))            
                px_last = self.df_px_last.loc[[date]].rename(index={date: nearest_date})
                px_volume = self.df_px_volume.loc[[date]].rename(index={date: nearest_date})
                returns = self.df_returns.loc[[date]].rename(index={date: nearest_date})
                volatility = self.df_volatility.loc[[date]].rename(index={date: nearest_date})

                tickers = self.df_compo[nearest_date].dropna().tolist()
                data[nearest_date] = pd.concat([px_last.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: PX_LAST}), 
                                            px_volume.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLUME}), 
                                            returns.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: RETURNS}),
                                            volatility.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLATILITY})]).T
                data[nearest_date][RFR] = self.risk_free_rate 
        return data

    def get_benchmark(self):
        data = {}
        for date in self.df_returns.index:
            nearest_date = min(pd.to_datetime(self.df_compo.columns), key=lambda x: abs(x - pd.to_datetime(date)))            
            px_last = self.df_px_last.loc[[date]].rename(index={date: nearest_date})
            px_volume = self.df_px_volume.loc[[date]].rename(index={date: nearest_date})
            returns = self.df_returns.loc[[date]].rename(index={date: nearest_date})
            volatility = self.df_volatility.loc[[date]].rename(index={date: nearest_date})
            tickers = self.df_compo[nearest_date].dropna().tolist()
            data[nearest_date] = pd.concat([px_last.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: PX_LAST}), 
                                        px_volume.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLUME}), 
                                        returns.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: RETURNS}),
                                        volatility.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLATILITY})]).T
            data[nearest_date][RFR] = self.risk_free_rate

            # Calculate equally distributed weights
            if len(tickers) > 0:
                equal_weight = 1 / len(tickers)
            else:
                equal_weight = 0
            data[nearest_date][WEIGHT] = equal_weight

            data[nearest_date][WEIGHTED_RETURNS] = data[nearest_date][WEIGHT] * data[nearest_date][RETURNS]
        return data
