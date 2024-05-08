import pandas as pd

VOLUME = "PX_VOLUME"
PX_LAST = "PX_LAST"
RETURNS = "RETURNS"
VOLATILITY = "VOLATILITY"
EXPECTED_RETURNS = "EXPECTED_RETURNS"

class Data:
    def __init__(self, path="", J=3):

        self.J = J  
        
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
        self.df_expected_returns = self.__calculate_expected_returns()
        
    def __treat_df(self, df, format):
        df.columns = df.columns.str.replace(" Equity", "")
        df.index = pd.to_datetime(df.index, format=format)
        return df.sort_index()

    def __calculate_returns(self):
        return self.df_px_last.apply(lambda column: column.ffill().pct_change(self.J, fill_method=None).dropna()) 
    
    def __calculate_volatility(self):
        df_volatility = self.df_returns.rolling(window=self.J).std()
        df_volatility.replace(0, pd.NA, inplace=True)
        return df_volatility.fillna(df_volatility.median())
    
    def __calculate_expected_returns(self):
        return self.df_returns.rolling(window=self.J).mean()

    def get_data(self, K:int=1):
        data = {}
        valid_index = self.df_px_last.index[self.J+1] 
        rebalance_dates = pd.date_range(valid_index, self.df_px_last.index[-1], freq=f'{K}ME')

        for date in rebalance_dates :
            if date in self.df_px_last.index:
                nearest_date = min(pd.to_datetime(self.df_compo.columns), key=lambda x: abs(x - pd.to_datetime(date)))            
                px_last = self.df_px_last.loc[[date]].rename(index={date: nearest_date})
                px_volume = self.df_px_volume.loc[[date]].rename(index={date: nearest_date})
                returns = self.df_returns.loc[[date]].rename(index={date: nearest_date})
                volatility = self.df_volatility.loc[[date]].rename(index={date: nearest_date})
                expected_returns = self.df_expected_returns.loc[[date]].rename(index={date: nearest_date})

                tickers = self.df_compo[nearest_date].dropna().tolist()
                data[nearest_date] = pd.concat([px_last.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: PX_LAST}), 
                                            px_volume.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLUME}), 
                                            returns.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: RETURNS}), 
                                            volatility.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLATILITY}), 
                                            expected_returns.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: EXPECTED_RETURNS})]).T
        return data
