import pandas as pd

compo = pd.read_excel('Data/Compo.xlsx', sheet_name="Compo")
compo.columns = pd.to_datetime(compo.columns, format='%Y%m%d')
# print(compo.columns)

def reading_df(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name, index_col=0)
    df.columns = df.columns.str.replace(" Equity", "").str.replace(" EQUITY", "")
    df = df.T #virer pour avoir les dates en index
    df.columns = pd.to_datetime(df.columns, format='%Y%m%d')
    ## Pourquoi mettre les dates en colonnes ?
    return df

## mettre les retraitements ici, mettre un bool US=True/false pour appliquer les listes d'exlusions
px_last_df = reading_df('Data/PX_Last_Volume.xlsm', sheet_name='PX_LAST')
px_volume_df = reading_df('Data/PX_Last_Volume.xlsm', sheet_name='PX_VOLUME')

result_dict = {}

for date in px_last_df.columns: # virer pour avoir les dates en index
    # print(date)
    # find the nearest date in compo for px_last_df and px_volume_df because the dates don't match
    nearest_date_px_last = min(compo.columns, key=lambda x: abs(x - date))
    nearest_date_px_volume = nearest_date_px_last  # Using the same nearest date for px_volume_df

    px_last_aligned = px_last_df[[date]].rename(columns={date: nearest_date_px_last})
    px_volume_aligned = px_volume_df[[date]].rename(columns={date: nearest_date_px_volume})
    tickers = compo[nearest_date_px_last].dropna().tolist()

    px_last_aligned = px_last_aligned.reindex(tickers).dropna().rename(columns={nearest_date_px_last: "PX_LAST"})
    px_volume_aligned = px_volume_aligned.reindex(tickers).dropna().rename(columns={nearest_date_px_volume: 'PX_VOLUME'})
    merged_df = pd.concat([px_last_aligned, px_volume_aligned], axis=1)

    result_dict[nearest_date_px_last] = merged_df

## NOTE 04/03: les données pour certains tickers de compo sont manquantes + on a la même compo tous les jours
    


print(result_dict[nearest_date_px_last])