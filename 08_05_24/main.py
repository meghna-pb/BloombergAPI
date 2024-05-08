import pandas as pd
from performance import Performance 
from data import Data
from signal_1 import Signal
from  optimisation import Optimisation


data = Data("Data").get_data() # Excel 
# data = Data().get_data() # Bloomberg

sig = Signal(data)

intersec, exemple_date = sig.create_intersections(10, 3)
portfolio_test = intersec[exemple_date]
print(portfolio_test["R1_V1"]) #["R1_V1"]
perf = Performance(intersec)
opt =  Optimisation(intersec)
full_returns = opt.get_full_returns()

# Visualisation : 
# perf.viewer(full_returns, 
#             portfolio_keys=None, 
#             #["R10-R1_V3-V1", "R1_V1", "R10_V3"]
#             )
 

# Tableau de résultats : 
tableau = perf.table(full_returns, ["R1", "R10", "R10-R1"], ["V1", "V3", "V3-V1"])
print(tableau)

"""
"At the beginning of each month all available stocks in the NYSE0AMEX are sorted independently 
based on past J month returns and divided into 10 portfolios. K represents monthly holding periods 
where K 5 three, six, nine, or 12 months."
-> Je sais pas comment integrer J et K ??? 
"""