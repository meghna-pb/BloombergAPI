import pandas as pd

class Data:
    def __init__(self, path=""): # exclusion:pd.DataFrame
        
        if path == "" : 
            # Pas testé, mais aucune raison que ca marche pas 
            from bloomberg import df_compo, dict_data
            self.df_compo = df_compo
            self.df_px_last = df_compo["PX_LAST"]
            self.df_px_volume = df_compo["PX_VOLUME"]
        else :
            self.df_compo = pd.read_excel(path+'/Bloomberg_Compo.xlsx', sheet_name="Compo")
            self.df_px_last = self.__reading_df(path+'/Bloomberg_Data.xlsx', sheet_name='PX LAST')
            self.df_px_volume = self.__reading_df(path+'/Bloomberg_Data.xlsx', sheet_name='PX VOLUME')

        self.df_compo.columns = pd.to_datetime(self.df_compo.columns, format='%Y%m%d')
        self.df_returns = self.__calculate_returns()
        self.df_exclusion = pd.DataFrame() # quand on aura le DF avec les titres à exclure
        

    def __reading_df(self, path, sheet_name):
        df = pd.read_excel(path, sheet_name=sheet_name, index_col=0)
        df.columns = df.columns.str.replace(" Equity", "")
        df.index = pd.to_datetime(df.index, format='%Y%m%d')       
        # if not df_exclusion is None:
        #     excluded_tickers = self.df_exclusion.index_tolist()
        #     df = df[~df.columns.isin(excluded_tickers)]
        return df
    

    def get_data(self): 
        data = {}
        for date in self.df_px_last.index:
            if date == self.df_px_last.index[0]:continue
            
            nearest_date = min(self.df_compo.columns, key=lambda x: abs(x - date)) 

            px_last_aligned = self.df_px_last.loc[[date]].rename(index={date: nearest_date})
            px_volume_aligned = self.df_px_volume.loc[[date]].rename(index={date: nearest_date})
            returns_aligned = self.df_returns.loc[[date]].rename(index={date: nearest_date})

            tickers = self.df_compo[nearest_date].dropna().tolist()
            
            px_last_aligned = px_last_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: "PX_LAST"})
            px_volume_aligned = px_volume_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: "PX_VOLUME"})
            returns_aligned = returns_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: "RETURNS"})

            merged_df = pd.concat([px_last_aligned, px_volume_aligned, returns_aligned]).T
            data[nearest_date] = merged_df
        return data
    
    
    def __calculate_returns (self) -> pd.DataFrame : 
        """
            calculates returns.
        """
        return self.df_px_last.apply(lambda colonne: colonne.ffill().pct_change(fill_method=None).dropna())