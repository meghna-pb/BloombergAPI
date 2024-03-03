
import pandas as pd
 
""" IMPORTATION DES DONNEES 

    ->> Insérer le code d'import des data avec bloom ici
    En attendant, on les récupère depuis des fichiers excel :) 
    
"""

# J'ai codé en brut hier mais ta fonction a toi est bcp plus pratique 

df_PX_LAST = pd.read_excel("Data/PX_Last_Volume.xlsm", sheet_name="PX_LAST", index_col=0)
df_PX_LAST.index = df_PX_LAST.index.strftime('%Y-%m') # Je garde pas le jour parce qu'il diffère chaque mois et on s'en fou 
df_PX_LAST.index = pd.to_datetime(df_PX_LAST.index)
df_PX_VOLUME = pd.read_excel("Data/PX_Last_Volume.xlsm", sheet_name="PX_VOLUME", index_col=0)
df_PX_VOLUME.index = df_PX_VOLUME.index.strftime('%Y-%m-%d')
df_PX_VOLUME.index = pd.to_datetime(df_PX_VOLUME.index)

# print(df_PX_LAST.describe())
# print(df_PX_VOLUME.describe())

#### +++ GESTION DES DONNEES MANQUANTES ? 

