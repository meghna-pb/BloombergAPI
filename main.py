import pandas as pd
from performance import Performance 
from data import Data
from signal_1 import Signal
from  optimisation import Optimisation


data = Data("Data").get_data()
sig = Signal(data)

intersec, exemple_date = sig.create_intersections(3, 2)
portfolio_test = intersec[exemple_date]
perf = Performance(intersec)
opt =  Optimisation(intersec)
full_returns = opt.get_full_returns()
print(full_returns) 

# Visualisation qui fonctionne ! 
perf.viewer(full_returns, 
            portfolio_keys= None, 
            #["R1_V2", "R1_V1", "R3_V2"]
            )


"""
    TO DO : 
    - Gerer la liste des exclusions (salle bloom)
    - Gerer les données manquantes -> Vérifier la date pour le bds (salle bloom)
"""