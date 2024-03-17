import pandas as pd
import matplotlib.pyplot as plt

from data import Data
from signal_1 import Signal
import optimisation


data = Data("Data").get_data()

sig = Signal(data)


###### Test intersection ######
intersec, exemple_date = sig.create_intersections(3, 2)
portfolio_test = intersec[exemple_date]
print(portfolio_test)

###### Test pondération equi : poids et rendements 
#portfolio_test_2 = optimisation.get_equal_weighted(portfolio_test)
#print(portfolio_test_2)
#return_test = optimisation.get_date_returns(portfolio_test)
#print(return_test)

###### Test calcul rendements sur toute les périodes : (marche pas)
# Tu peux tout modifier comme tu veux de tout facon pas sure qu'il y ait des trucs bon a garder 
#portfolio_test = intersec[exemple_date]
#optimisation.get_full_returns(portfolio_test)


"""
    TO DO : 
    - Gerer la liste des exclusions (salle bloom)
    - Gerer les données manquantes -> Vérifier la date pour le bds (salle bloom)
    
    - Trier l'index des data 
    - Tracer la perf -> Rebalancement tous les mois // faire un df par ptf (R1_V1, ...) pour toute les dates
    - 
"""