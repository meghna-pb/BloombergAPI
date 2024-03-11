import pandas as pd

# Remarque Caro : j'ai changé le nom des variables (name_type ->>> type_name)
# Juste pour plaire à Celia, elle avait dit qu'elle aimait ca comme ca et si ca peut lui faire plaisir on va pas cracher dessus... 

class Data:
    def __init__(self, path): #exclusion:pd.DataFrame
        self.df_compo = pd.read_excel(path+'/Compo.xlsx', sheet_name="Compo")
        self.df_compo.columns = pd.to_datetime(self.df_compo.columns, format='%Y%m%d')
        self.df_px_last = self.__reading_df(path+'/PX_Last_Volume.xlsm', sheet_name='PX_LAST')
        self.df_px_volume = self.__reading_df(path+'/PX_Last_Volume.xlsm', sheet_name='PX_VOLUME')
        self.df_returns = self.__calculate_returns()
        self.df_exclusion = pd.DataFrame() # quand on aura le DF avec les titres à exclure

    def __reading_df(self, path, sheet_name, US=False):
        df = pd.read_excel(path, sheet_name=sheet_name, index_col=0)
        df.columns = df.columns.str.replace(" Equity", "").str.replace(" EQUITY", "")
        df.index = pd.to_datetime(df.index, format='%Y%m%d')
        if US: 
            excluded_tickers = self.df_exclusion.index.tolist()
            df = df[~df.columns.isin(excluded_tickers)]
        return df
    
        # en fait, à la place de faire un booleen US/not US, 
        # on peut initialiser df_exclusion en None et faire la condition sur ca ? 
        # comme ca, si on veut filtrer un indice meme hors US on peut ? 
        
        #if not df_exclusion is None:
        #    excluded_tickers = self.df_exclusion.index_tolist()
        #    df = df[~df.columns.isin(excluded_tickers)]
    

    def get_data(self): 
        data = {}
        for date in self.df_px_last.index:
            if date == self.df_px_last.index[0]:continue
            # gestion du décalage pour le df des rendements (pas la première date)
            
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
        # return self.df_px_last.apply(lambda colonne: colonne.pct_change().dropna())
        return self.df_px_last.apply(lambda colonne: colonne.ffill().pct_change().dropna())
    

# ## NOTE 04/03: les données pour certains tickers de compo sont manquantes + on a la même compo tous les jours
# Remarque Caro : actuellement, les rendements sont faussés par les données manquantes 
    


