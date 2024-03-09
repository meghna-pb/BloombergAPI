
import pandas as pd
 
""" IMPORTATION ET TRAITEMENT DES DONNEES 

    ->> Insérer le code d'import des data avec bloom ici
    En attendant, on les récupère depuis des fichiers excel :) 
    
    PS : actuellement, les données pour certains tickers sont manquantes 
    + On a la même compo chaque mois (c'est pas normal)

"""

def reading_df(path:str, sheet_name:str) -> pd.DataFrame:
    # Fonction utile seulement sans bloomberg 
    df = pd.read_excel(path, sheet_name=sheet_name, index_col=0)
    df.columns = df.columns.str.replace(" Equity", "").str.replace(" EQUITY", "") 
    # df = df.T # -> dates en colonnes 
    df.index = pd.to_datetime(df.index, format='%Y%m%d')
    return df


def get_returns (px_last:pd.DataFrame) -> pd.DataFrame : 
    """
         calculates returns.
         
         Je sais c'est pas très logique de le mettre la mais comme ca on peut l'avoir dans tes dictionnaires par dates ? 
    """
    return px_last.apply(lambda colonne: colonne.pct_change().dropna())


def get_nearest_date(returns:pd.DataFrame, px_volume:pd.DataFrame, compo:pd.DataFrame) -> dict :
    # Find the nearest date in compo for px_last_df and px_volume_df if the dates don't match 
    
    # Maybe c'est mieux de mettre les 2 df (PX last, PX Volume et returns) ? 
    # Je sais pas si plus tard on aura besoin que des rendements ou si le PX_Last peut encore nous servir ? 
    
    result_dict = {}

    for date in returns.index:
        nearest_date = min(compo.columns, key=lambda x: abs(x - date))

        px_last_aligned = returns.loc[[date]].rename(index={date: nearest_date})
        px_volume_aligned = px_volume.loc[[date]].rename(index={date: nearest_date})
        
        tickers = compo[nearest_date].dropna().index.tolist()

        #px_last_aligned = px_last_aligned.reindex(tickers).dropna().rename(index={nearest_date: "PX_LAST"})
        #px_volume_aligned = px_volume_aligned.reindex(tickers).dropna().rename(index={nearest_date: 'PX_VOLUME'})
        # Pas compris a quoi sa sert et ca fait tout bugger 
        
        merged_df = pd.concat([px_last_aligned, px_volume_aligned], axis=0)
        merged_df = merged_df.transpose()
        merged_df.columns = ["RETURNS", "PX_VOLUME"]
        
        result_dict[nearest_date] = merged_df

    return result_dict, nearest_date

        
 
df_px_last = reading_df('Data/PX_Last_Volume.xlsm', sheet_name='PX_LAST')
df_px_volume = reading_df('Data/PX_Last_Volume.xlsm', sheet_name='PX_VOLUME')
## ++ Mettre les retraitements ici : un bool US=True/false pour appliquer les listes d'exlusions
#### +++ GESTION DES DONNEES MANQUANTES ? 

df_returns = get_returns(df_px_last)

df_compo = pd.read_excel('Data/Compo.xlsx', sheet_name="Compo")
df_compo.columns = pd.to_datetime(df_compo.columns, format='%Y%m%d')

#### TEST :    
results, exemple_date = get_nearest_date(df_returns, df_px_volume, df_compo)
print(results[exemple_date])


# print(df_px_last.describe())
# print(df_px_volume.describe())
# print(df_returns.describe())

