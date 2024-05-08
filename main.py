from data import Data, RETURNS, VOLUME
from signals import Signal
from optimisation import Optimisation
from performance import Performance

import pandas as pd


### IMPORTATION ET PREMIER TRAITEMENT DES DONNEES ###

data = Data(path="Data", J=3) # .get_data() # Excel
# data = Data(J=1) # Bloomberg

""" Ici, on ne fait que récupérer les données et caluler les rendements. 
Sorties = df_returns, df_px_last, df_px_volume. """


### CREATION DES PORTEFEUILLES ###

test_date = pd.Timestamp('2024-02-16 00:00:00')

signal = Signal(data=data, K=3, n_returns=10, m_volume=3)
simple_returns, simple_volume = signal.create_simple_portfolios()
# print(simple_volume[test_date])

### CALCUL DES PONDERATIONS ###

optim = Optimisation(returns_portfolios=simple_returns, volume_portfolios=simple_volume)

# Equipondération : 
# equi_weighted_returns = optim.get_equal_weight(simple_returns.copy())
# equi_weighted_volume = optim.get_equal_weight(simple_volume.copy())
# print(equi_weighted_returns)

# 1/vol (vol glissante sur K mois) :
vol_weighted_returns = optim.get_scaling_weight(simple_returns.copy())
vol_weighted_volume = optim.get_scaling_weight(simple_volume.copy())
# print(vol_weighted_returns)

# Optimisation des méthodes : 
# best_returns, best_volume = optim.get_weighted_returns()
# print(best)

### CREATIONS DES PORTEFEUILLES CROISES ###

intersection = signal.create_intersected_portfolios(returns_ptf=vol_weighted_returns, volume_ptf=vol_weighted_volume)
full_returns = optim.get_full_returns(intersection)
# print(full_returns)


### PERFORMANCE ###

perf = Performance(portfolio=intersection)

perf.viewer(full_returns, portfolio_keys=None)

# table = perf.table(full_returns, ["R1", "R5", "R10", "R10-R1"], ["V1", "V2", "V3", "V3-V1"])
# print(table)


"""
    Rappel Caro : 
    - Probleme date intersection avec best weight ??? 
    - Commentaire code ! 
"""