import pandas as pd

VOLUME = "PX_VOLUME"  
PX_LAST = "PX_LAST"
RETURNS = "RETURNS"

class Data:
    def __init__(self, path=""): # exclusion:pd.DataFrame
        
        if path == "" : 
            from bloomberg import df_compo, dict_data
            self.df_compo = df_compo
            self.df_px_last = dict_data[PX_LAST].sort_index()
            self.df_px_volume = dict_data[VOLUME].sort_index()
        else :
            self.df_compo = pd.read_excel(path+'/Bloomberg_Compo.xlsx', sheet_name="Compo")
            self.df_px_last = pd.read_excel(path+'/Bloomberg_Data.xlsx', sheet_name='PX LAST', index_col=0)
            self.df_px_volume = pd.read_excel(path+'/Bloomberg_Data.xlsx', sheet_name='PX VOLUME', index_col=0)
    
        self.df_px_last = self.__treat_df(self.df_px_last, format='%Y%m%d')
        self.df_px_volume = self.__treat_df(self.df_px_volume, format='%Y%m%d')
        self.df_compo.columns = pd.to_datetime(self.df_compo.columns, format='%Y%m%d')
        self.df_returns = self.__calculate_returns()
        
    def __treat_df(self, df, format):
        df.columns = df.columns.str.replace(" Equity", "")
        df.index = pd.to_datetime(df.index, format=format)
        return df.sort_index()
    

    def get_data(self): 
        data = {}
        for date in self.df_px_last.index:
            if date == self.df_px_last.index[0]:continue
            nearest_date = min(pd.to_datetime(self.df_compo.columns), key=lambda x: abs(x - pd.to_datetime(date))) 
            px_last_aligned = self.df_px_last.loc[[date]].rename(index={date: nearest_date})
            px_volume_aligned = self.df_px_volume.loc[[date]].rename(index={date: nearest_date})
            returns_aligned = self.df_returns.loc[[date]].rename(index={date: nearest_date})

            tickers = self.df_compo[nearest_date].dropna().tolist()
            # tickers = [ticker.replace(" Equity", "") for ticker in self.df_compo[nearest_date].dropna().tolist()]
            # tickers = [str(ticker) + " Equity" for ticker in self.df_compo[nearest_date].dropna().tolist()]
            px_last_aligned = px_last_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: PX_LAST})
            px_volume_aligned = px_volume_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLUME})
            returns_aligned = returns_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: RETURNS})

            merged_df = pd.concat([px_last_aligned, px_volume_aligned, returns_aligned]).T
            data[nearest_date] = merged_df
        return data
    
    
    def __calculate_returns (self) -> pd.DataFrame : 
        """
            calculates returns.
        """
        return self.df_px_last.apply(lambda colonne: colonne.ffill().pct_change(fill_method=None).dropna())