from tools import run_excel, run_app

nb_periods = 3
rebalancing_interval = 6
nb_returns_based_ptf = 10
nb_volume_based_ptf = 5
risk_free_rate = 0.2
ponderation_method = "equi"
file_name = "inputs_port"

run_excel(J=nb_periods, 
          K=rebalancing_interval, 
          n=nb_returns_based_ptf, 
          m=nb_volume_based_ptf, 
          risk_free_rate=risk_free_rate, 
          ponderation_method=ponderation_method) 


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