from tools import run_excel, run_grid_search, run_app

nb_periods = 4
rebalancing_interval = 12
nb_returns_based_ptf = 10
nb_volume_based_ptf = 3
risk_free_rate = 0.015
ponderation_method = "volumexprice"
# file_name = "inputs_port"

run_excel(J = nb_periods, 
          K = rebalancing_interval, 
          n = nb_returns_based_ptf, 
          m = nb_volume_based_ptf, 
          risk_free_rate = risk_free_rate, 
          ponderation_method=ponderation_method) 


########## Recherche des meilleurs paramètres : ##########  

# J_values = [2, 3, 4, 5]
# K_values = [3, 6, 9, 12]
# n_values = [3, 5, 10, 15]
# m_values = [3, 5, 10, 15]
# risk_free_rate = 0.015
# ponderation_methods = ["equi", "vol", "volume", "volumexprice"]

# run_grid_search(J_values, K_values, n_values, m_values, risk_free_rate, ponderation_methods)

