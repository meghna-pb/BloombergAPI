import pandas as pd
from performance import Performance 
from data import Data
from signal_1 import Signal
from  optimisation import Optimisation


data = Data("Data").get_data()
sig = Signal(data)

intersec, exemple_date = sig.create_intersections(2, 2)
portfolio_test = intersec[exemple_date]
print(portfolio_test) #["R1_V1"]
perf = Performance(intersec)
opt =  Optimisation(intersec)
full_returns = opt.get_full_returns()

"""
    J'ai un doute sur certains ptf long/short : 
    Quand on a une intersection entre un ptf long et un long/short, potentiellement il y a des actions qui sont à la fois long et short 
    Donc j'ai laissé 2 fois la ligne avec une position différente ? 
    
    # Ok en fait, ca c'est ce que j'ai essayé de faire, en vrai ca marche pas encore et j'en ai mare :( 

"""

# Visualisation qui fonctionne ! 
perf.viewer(full_returns, 
            portfolio_keys=None, 
            #["R10-R1_V3-V1", "R1_V1", "R10_V3"]
            )
# J'arrive pas a filtrer sur les ptf long short en même temps que les normaux mais ils apparaissent bien quand je les sort tous...
 

# Pour avoir un tableau de résultats comme dans l'article : 
# tableau = perf.table(full_returns, ["R1", "R10", "R10-R1"], ["V1", "V3", "V3-V1"])
# print(tableau)

"""
"At the beginning of each month all available stocks in the NYSE0AMEX are sorted independently 
based on past J month returns and divided into 10 portfolios. K represents monthly holding periods 
where K 5 three, six, nine, or 12 months."
-> Je sais pas comment integrer J et K ??? 
"""


"""
    TO DO : 
    - Gerer la liste des exclusions (salle bloom)
    - Gerer les données manquantes -> Vérifier la date pour le bds (salle bloom)
    
    PS : SENS DES PTF INVERSE COMME DANS L ARTICLE 
    -> R1 = looser, Rn = winner 
"""