import pandas as pd
from signal_caro import Signal

# compo = pd.read_excel('Data/Compo.xlsx', sheet_name="Compo")
# compo.columns = pd.to_datetime(compo.columns, format='%Y%m%d')
# print(compo.columns)

class Data:
    def __init__(self, path):
        self.compo = pd.read_excel(path+'/Compo.xlsx', sheet_name="Compo")
        self.compo.columns = pd.to_datetime(self.compo.columns, format='%Y%m%d')
        self.px_last_df = self.__reading_df(path+'/PX_Last_Volume.xlsm', sheet_name='PX_LAST')
        self.px_volume_df = self.__reading_df(path+'/PX_Last_Volume.xlsm', sheet_name='PX_VOLUME')
        self.exclusion = pd.DataFrame() # quand on aura le DF avec les titres à exclure
        self.result_dict = {}

    def __reading_df(self, path, sheet_name, US=False):
        df = pd.read_excel(path, sheet_name=sheet_name, index_col=0)
        df.columns = df.columns.str.replace(" Equity", "").str.replace(" EQUITY", "")
        df.index = pd.to_datetime(df.index, format='%Y%m%d')
        if US: 
            excluded_tickers = self.exclusion.index.tolist()
            df = df[~df.columns.isin(excluded_tickers)]
        return df

    def __align_data(self): 
        for date in self.px_last_df.index:
            nearest_date_px_last = min(self.compo.columns, key=lambda x: abs(x - date)) 
            nearest_date_px_volume = nearest_date_px_last  # Using the same nearest date for px_volume_df

            px_last_aligned = self.px_last_df.loc[[date]].rename(index={date: nearest_date_px_last})
            px_volume_aligned = self.px_volume_df.loc[[date]].rename(index={date: nearest_date_px_volume})

            tickers = self.compo[nearest_date_px_last].dropna().tolist()
            px_last_aligned = px_last_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date_px_last: "PX_LAST"})
            px_volume_aligned = px_volume_aligned.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date_px_last: "PX_VOLUME"})
            merged_df = pd.concat([px_last_aligned, px_volume_aligned])
            self.result_dict[nearest_date_px_last] = merged_df
        return self.result_dict
    
    
    def calculate_returns(self):
        """
         calculates returns.
        """
        if not self.result_dict:  
            self.__align_data()
        prev_df = None
        updated_result_dict = {}
        for date, df in self.result_dict.items():
            if prev_df is not None:
                current_px_last_row = df.loc['PX_LAST']
                prev_px_last_row = prev_df.loc['PX_LAST']

                returns_row = (current_px_last_row / prev_px_last_row) - 1
                df.loc['returns'] = returns_row

                updated_result_dict[date] = df

            prev_df = df

        return updated_result_dict


# ## NOTE 04/03: les données pour certains tickers de compo sont manquantes + on a la même compo tous les jours
    


