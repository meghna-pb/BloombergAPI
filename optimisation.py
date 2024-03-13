import pandas as pd
import numpy as np
from scipy.optimize import minimize


def get_equal_weighted(portfolio:pd.DataFrame) -> pd.DataFrame :
    nb_shares = len(portfolio)

    # Equal-weight calculation
    weight = 1 / nb_shares
    
    # Add Equal-weight column to DataFrame
    portfolio['WEIGHTS'] = weight
    portfolio['WEIGHTED_RETURNS'] = portfolio['RETURNS'] * portfolio['WEIGHTS']

    return portfolio

def get_date_returns(portfolio:pd.DataFrame) -> float : 
    """
    Function to calculate the portfolio return for a specific date based on the "WEIGHTED_RETURNS" column.

    :param portfolio: DataFrame containing "WEIGHTED_RETURNS" columns.
    """
    return portfolio['WEIGHTED_RETURNS'].sum()


###### ne fonctionne pas, et je suis pas sure de ce que j'essaie de faire alors je m'arrete la --> on en reparle demain je comprends pas non plus ! 
# parce qu'en soit si on a les rendements pondérés on a pas besoin de la fonction en dessous on met juste le nom du ptf et on trace non? à quoi sert cette fonction?


def get_full_returns(portfolios:dict) :
    returns = {}
    for date, date_portfolios in portfolios.items(): 
        #print(date_portfolios["R1_V1"]) 
        date_portfolio = date_portfolios["R1_V1"] ############# nom ptf a mettre en arg
        returns[date] = get_date_returns[date_portfolio]
        
    return pd.DataFrame(returns, columns = "RETURNS")

        
        