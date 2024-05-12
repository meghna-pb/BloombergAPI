from data import Data
from signals import Signal
from optimisation import Optimisation
from performance import Performance

import pandas as pd


#################################### IMPORTATION ET PREMIER TRAITEMENT DES DONNEES ####################################

# data = Data(path="Data", J=3, risk_free_rate=0.2) # .get_data() # Excel
# data = Data(J=1, risk_free_rate=0.2) # Bloomberg

""" 
-> Récupération des données brutes (depuis Excel ou Bloomberg)
-> Mise en forme dans des dataframes spécifiques : 
    - df_returns - df_px_last - df_px_volume - df_volatility - ... 
    
-> Remarque :
    - La fonction "get_data" qui créé un dict/df par date avec toute les données (returns, px_last, vol, ...)
        # est appelée dans le signal 
    - Verifier la formule volatilité + expected_returns (pour sharpe)
    - Pas bon si J=1
    
"""


############################################# CREATION DES PORTEFEUILLES ##############################################

# test_date = pd.Timestamp('2024-02-16 00:00:00')
# La date test fonctionne seulement si J=3, K=3 

# signal = Signal(data=data, K=3, n_returns=3, m_volume=2)
# simple_returns, simple_volume = signal.create_simple_portfolios()
# print(simple_volume[test_date])

"""
-> Tri des données et création des portefeuilles "simple" selon le rendements / volume (ptf Rn et Vm)
-> Ajout des portefeuilles long/short (pour les extremes Rn-R1 et Vm-V1)
"""


############################################### CALCUL DES PONDERATIONS ###############################################

### CALCUL DES PONDERATIONS ###

# optim = Optimisation(returns_portfolios=simple_returns, volume_portfolios=simple_volume)

# Equipondération : 
# equi_weighted_returns = optim.get_equal_weight(simple_returns.copy())
# equi_weighted_volume = optim.get_equal_weight(simple_volume.copy())
# print(equi_weighted_returns)

# 1/vol (vol glissante sur K mois) :
# vol_weighted_returns = optim.get_scaling_weight(simple_returns.copy())
# vol_weighted_volume = optim.get_scaling_weight(simple_volume.copy())
# print(vol_weighted_returns)

# Sharpe ratio :
# sharpe_weighted_returns = optim.get_sharpe_weight(simple_returns.copy())
# sharpe_weighted_volume = optim.get_sharpe_weight(simple_volume.copy())
# print(sharpe_weighted_returns)

# Optimisation des méthodes : 
# best_returns, best_volume = optim.get_weighted_returns()
# print(best_volume)

"""
-> Calcul des pondérations pour les portefeuilles simples et long/short 
-> Plusieurs méthodes de pondérations : equipondéré, 1/vol, sharpe ratio
-> Une méthode qui les test toute et ressort les résultats de la meilleure. 

Rq : 
    - On peut evidement rajouter d'autres méthondes de pondérations (Markowitz ou autre)
    - La méthode optimale de pondération n'est pas necessairement la même pour returns et volume
    - La méthode optimale est celle qui maximise la somme total sur tous les portefeuilles (R ou V) et sur tout les periodes
"""


######################################### CREATION DES PORTEFEUILLES CROISES ##########################################

# intersection = signal.create_intersected_portfolios(returns_ptf=best_returns, volume_ptf=best_volume)
# full_returns = optim.get_full_results(intersection)
# print(full_returns)

"""
-> Création de portefeuilles croisés à partir des portefeuilles simples et long/short 
-> Calcul des rendements totaux par portefeuille et par date 

Rq : 
    - Chaque portefeuille est déja pondéré, la pondération du ptf croisé est la somme des pondérations des deux composantes 
"""


##################################################### PERFORMANCE #####################################################

# perf = Performance(portfolio=intersection)

# Graphique : 
# perf.viewer(full_returns, portfolio_keys=None)

# Tableau : 
# table = perf.table(full_returns, ["R1", "R5", "R10", "R10-R1"], ["V1", "V2", "V3", "V3-V1"])
# print(table)

"""
-> A partir des rendements totaux des portefeuilles croisés, affiche les résultats (graphique et/ou tableau) 

A rajouter : métrique de performance
"""



""" Petit recap global : 
- J'ai rajouté les variables J et K (J = nombre d'observations dans les calculs, K = fréquence de rebalancement)
- Je pense que toute la partie data / signal / optim est opérationnelle, sauf si tu veux rajouter des trucs ? 
- Il nous reste à faire toute la partie perf pour laquelle on a que des visualisations pour l'instant 
    -> Ajout du calcul de plusieurs metriques de perf (certains codes sont déjà fait dans les anciennes versions)
    -> Ajout d'une méthode qui choisis la meilleure méthode de ponderation ? 
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
        weighted_returns = optim.get_scaling_weight(simple_returns.copy())
        weighted_volume = optim.get_scaling_weight(simple_volume.copy())
    elif ponderation_method == "sharpe" :
        weighted_returns = optim.get_sharpe_weight(simple_returns.copy())
        weighted_volume = optim.get_sharpe_weight(simple_volume.copy())
        
    intersection = signal.create_intersected_portfolios(returns_ptf=weighted_returns, volume_ptf=weighted_volume)
    full_returns = optim.get_full_results(intersection)

    perf = Performance(portfolio=intersection)
    # perf.viewer(full_returns, portfolio_keys=None)
    perf.cumulative_viewer(full_returns)
    # table = perf.table(full_returns, ["R1", "R5", "R10", "R10-R1"], ["V1", "V2", "V3", "V3-V1"])
    # print(table)
    
    # print(perf.sharpe_ratio_meghna(risk_free_rate)) # Meghna
    print(perf.sharpe_ratio(full_returns=full_returns, risk_free_rate=risk_free_rate)) # Caro
    # print(perf.VaR_meghna(confidence_level=0.95)) # Meghna 
    print(perf.value_at_risk(full_returns=full_returns, confidence_level=0.95)) # Caro
    
test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="equi") # -> OK
# test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="vol") # -> OK
# test(J=3, K=3, n=3, m=2, risk_free_rate=0.2, ponderation_method="sharpe") # -> OK

# Remarque : je pense que ca serait plus smart de calculer les full_returns directement dans la classe perf ? 