from data import Data
from signals import Signal
from optimisation import Optimisation, WEIGHT
from performance import Performance
from charts import Charts

import pandas as pd

""" 
Explication des étapes : 

1) IMPORTATION ET PREMIER TRAITEMENT DES DONNEES -> classe data :  
    - Récuparation des données brutes (depuis Excel ou Bloomberg), 
    - Mise en forme dans des dataframes spécifiques : df_returns, df_px_last, df_volume, df_volatility
Remarques : 
    - La fonction "get_data" qui créé un dict/df par date avec les données (returns, px_last, ...) est appelée dans le signal 
    - Pas bon si J = 1
    
2) CREATION DES PORTEFEUILLE -> classe signal : 
    - Tri des données par rendements et volume
    - Création de porefeuilles "simples" = ptf Rn et Vm
    - Ajout des portefeuilles Long/Short (pour les extrèmes Rn-R1 et Vm-V1)

3) CALCUL DES PONDERATIONS -> classe optimisation : 
    - calcul des pondérations pour les portefeuilles simples et long/short 
    - 3 types de pondérations : équipondérée, 1/vol, sharpe ratio???, volume, prix*volume
    
4) CREATION DES PORTEFEUILLES CROISES -> classes signal & optim : 
    - Création de portefeuilles croisés à partir des portefeuilles simples et long/short 
    - Calcul des rendements totaux par portefeuille et par date 
Remarques : Chaque portefeuille est déja pondéré, la pondération du ptf croisé est la somme des pondérations des deux composantes

5) CALCUL DES PERFORMANCES -> classe performance : 
    - calcul de toute les métriques (VaR, perf, vol, sharpe, ...)
    - renvoie des dictionnaires (un chiffre pour chaque ptf)

6) Graph/Tableau des résultats -> classe charts :
    - Hérite de la classe perf et renvoie les chiffres bien formatés + graphs 

"""

def export_to_excel(intersected_portfolios, filename="inputs_port.xlsx"):
    """
    Export all intersected portfolios to a single Excel sheet.
    
    :param intersected_portfolios: Dictionary of intersected portfolios.
    :param filename: The filename for the resulting Excel file.
    """
    combined_data = pd.DataFrame()
    
    for date, portfolios in intersected_portfolios.items():
        for ptf_name, ptf_data in portfolios.items():
            temp_df = pd.DataFrame()
            temp_df['Date'] = [date.strftime('%d/%m/%Y')] * len(ptf_data)  
            temp_df['SECURITY_ID'] = ptf_data.index  
            temp_df['QUANTITY'] = ptf_data[WEIGHT].values
            temp_df['PORTFOLIO NAME'] = ptf_name 
            combined_data = pd.concat([combined_data, temp_df], ignore_index=True)
    
    combined_data.to_excel(filename, index=False)


##### Fonction de test : ####

def test(J, K, n, m, risk_free_rate, ponderation_method) :
    data = Data(path="Data", J=J, risk_free_rate=risk_free_rate) 
    bench = data.get_benchmark()
    rfr = 0.2
    
    signal = Signal(data=data, K=K, n_returns=n, m_volume=m)
    simple_returns, simple_volume = signal.create_simple_portfolios()
    
    optim = Optimisation(returns_portfolios=simple_returns, 
                         volume_portfolios=simple_volume,
                         risk_free_rate=rfr)
    if ponderation_method == "equi" :
        weighted_returns = optim.get_equal_weight(simple_returns.copy())
        weighted_volume = optim.get_equal_weight(simple_volume.copy())
    elif ponderation_method == "vol" :
        weighted_returns = optim.get_inverse_volatility_weight(simple_returns.copy())
        weighted_volume = optim.get_inverse_volatility_weight(simple_volume.copy())
    elif ponderation_method == "volume":
        weighted_returns = optim.get_volume_weight(simple_returns.copy())
        weighted_volume = optim.get_volume_weight(simple_volume.copy())
    elif ponderation_method == "volumexprice":
        weighted_returns = optim.get_dollar_volume_weight(simple_returns.copy())
        weighted_volume = optim.get_dollar_volume_weight(simple_volume.copy())
    elif ponderation_method == "best" :
        weighted_returns = optim.get_best_weighting_method(simple_returns.copy())
        weighted_volume = optim.get_best_weighting_method(simple_volume.copy())
    
    intersection = signal.create_intersected_portfolios(returns_ptf=weighted_returns, volume_ptf=weighted_volume)
    export_to_excel(intersection)
    full_results = optim.get_full_results(intersection)

    # charts = Charts(portfolios=full_results, bench=bench, risk_free_rate=rfr, confidence_level=0.05)
    # charts.get_figures("Tracking Error")
    # charts.viewer(portfolio_keys=None)
    # charts.cumulative_viewer(portfolio_keys=None)
    # print(charts.get_table()) # portfolio_keys=['R1_V1', 'R2_V1', 'R1_V2', 'R2_V2'])

    
# test(J=3, K=3, n=5, m=3, risk_free_rate=0.2, ponderation_method="best") # -> OK
# test(J=3, K=3, n=2, m=2, risk_free_rate=0.2, ponderation_method="equi") # -> OK
test(J=3, K=3, n=7, m=5, risk_free_rate=0.2, ponderation_method="vol") # -> OK
# test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="volume") # -> OK
# test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="volumexprice") # -> OK



### Vérifier les perfs annualisées ? 
