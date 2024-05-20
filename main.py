from data import Data
from signals import Signal
from optimisation import Optimisation
from performance import Performance
from charts import Charts

# import pandas as pd

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


##### Fonction de test : ####

def test(J, K, n, m, risk_free_rate, ponderation_method) :
    data = Data(path="Data", J=J, risk_free_rate=risk_free_rate) 
    
    signal = Signal(data=data, K=K, n_returns=n, m_volume=m)
    simple_returns, simple_volume = signal.create_simple_portfolios()
    
    optim = Optimisation(returns_portfolios=simple_returns, volume_portfolios=simple_volume)
    if ponderation_method == "equi" :
        weighted_returns = optim.get_equal_weight(simple_returns.copy())
        weighted_volume = optim.get_equal_weight(simple_volume.copy())
    elif ponderation_method == "vol" :
        weighted_returns = optim.get_inverse_volatility_weight(simple_returns.copy())
        weighted_volume = optim.get_inverse_volatility_weight(simple_volume.copy())
    elif ponderation_method == "sharpe" :
        weighted_returns = optim.get_sharpe_weight(simple_returns.copy())
        weighted_volume = optim.get_sharpe_weight(simple_volume.copy())
    elif ponderation_method == "volume":
        weighted_returns = optim.get_volume_weight(simple_returns.copy())
        weighted_volume = optim.get_volume_weight(simple_volume.copy())
    elif ponderation_method == "volumexprice":
        weighted_returns = optim.get_dollar_volume_weight(simple_returns.copy())
        weighted_volume = optim.get_dollar_volume_weight(simple_volume.copy())
    
    intersection = signal.create_intersected_portfolios(returns_ptf=weighted_returns, volume_ptf=weighted_volume)
    full_results = optim.get_full_results(intersection)

    # # perf = Performance(portfolios=full_results)
    
    charts = Charts(portfolios=full_results)
    charts.viewer(portfolio_keys=None)
    # charts.cumulative_viewer(portfolio_keys=None)
    print(charts.get_figures()) # portfolio_keys=['R1_V1', 'R2_V1', 'R1_V2', 'R2_V2'])

    
    
# test(J=3, K=3, n=2, m=2, risk_free_rate=0.2, ponderation_method="equi") # -> OK
test(J=3, K=3, n=2, m=2, risk_free_rate=0.2, ponderation_method="vol") # -> OK
# test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="sharpe") # -> Nooooooooooooooooooooooo
# test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="volume") # -> OK
# test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="volumexprice") # -> OK


""" 
Les résultats pour toute les métriques sont atroces, je pense faut vraiment revoir la création des ptf :(
    (surtout les 3 premiers ptf)
    
Les portefeuilles avec pondération sharpe sont attroces, je propose qu'on les enlève...  
Par contre ma fonction qui cherche la meilleure pondération je peux la faire en maximisant le ratio de sharpe (calculé dans les perf) ?  

Ducoup j'ai rajouté d'autre pondérations un peu bateau 
"""

