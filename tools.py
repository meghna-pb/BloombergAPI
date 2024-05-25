from data import Data
from signals import Signal
from optimisation import Optimisation, WEIGHT
from charts import Charts

from datetime import datetime
import pandas as pd


def export_to_excel(intersected_portfolios:dict, start_date:str, end_date:str, filename:str="inputs_port"):
    """
    Export all intersected portfolios to a single Excel sheet, filtering entries by a specified date range.

    :param intersected_portfolios: Dictionary of intersected portfolios.
    :param start_date: The start date for the date filter as a string in 'dd/mm/yyyy' format.
    :param end_date: The end date for the date filter as a string in 'dd/mm/yyyy' format.
    :param filename: The filename for the resulting Excel file.
    """
    start_date = datetime.strptime(start_date, '%d/%m/%Y')
    end_date = datetime.strptime(end_date, '%d/%m/%Y')
    
    combined_data = pd.DataFrame()
    
    for date, portfolios in intersected_portfolios.items():
        if start_date <= date <= end_date:
            for ptf_name, ptf_data in portfolios.items():
                temp_df = pd.DataFrame()
                temp_df['Date'] = [date.strftime('%d/%m/%Y')] * len(ptf_data)
                temp_df['SECURITY_ID'] = ptf_data.index
                temp_df['QUANTITY'] = ptf_data['WEIGHT'].values
                temp_df['PORTFOLIO NAME'] = ptf_name
                combined_data = pd.concat([combined_data, temp_df], ignore_index=True)
    
    combined_data.to_csv(filename + ".csv", index=False)


def run_excel(J:int, K:int, n:int, m:int, risk_free_rate:float, ponderation_method:str, filename:str=None) :
    """
    Executes the full analysis pipeline for optimizing and evaluating investment portfolios based on specified weighting methods. 
    This function incorporates steps from data fetching and signal processing to portfolio optimization, intersection, and comprehensive visualization of results.

    :param J: Integer representing the number of periods used for calculating rolling statistics.
    :param K: Integer specifying the rebalancing interval for the portfolios in months.
    :param n: Integer indicating the number of return-based portfolios to be generated.
    :param m: Integer indicating the number of volume-based portfolios to be generated.
    :param risk_free_rate: Float representing the risk-free rate used in financial calculations.
    :param ponderation_method: String specifying the weighting method to be applied to the portfolios. 
    :param filename: Optional string. If provided, specifies the filename where the Excel output of intersected portfolios will be saved. If None, no file is saved.

    :return: None. Directly prints and displays portfolio performance results and visualizations.
    """
    
    data = Data(path="Data", J=J, risk_free_rate=risk_free_rate) 
    bench = data.get_benchmark()
    rfr = risk_free_rate
    
    signal = Signal(data=data, K=K, n_returns=n, m_volume=m)
    simple_returns, simple_volume = signal.create_simple_portfolios()
    
    optim = Optimisation(returns_portfolios=simple_returns, 
                         volume_portfolios=simple_volume,
                         risk_free_rate=rfr)
    ponderation_methods = {"equi": optim.get_equal_weight,
                           "vol": optim.get_inverse_volatility_weight,
                           "volume": optim.get_volume_weight,
                           "volumexprice": optim.get_dollar_volume_weight, 
                            "best" :optim.get_best_weighting_method }

    if ponderation_method in ponderation_methods:
        weight_function = ponderation_methods[ponderation_method]
        weighted_returns = weight_function(simple_returns.copy())
        weighted_volume = weight_function(simple_volume.copy())
    else:
        raise ValueError(f"Invalid ponderation method: {ponderation_method}")
    
    intersection = signal.create_intersected_portfolios(returns_ptf=weighted_returns, volume_ptf=weighted_volume)
    if not filename is None :
        export_to_excel(intersected_portfolios=intersection, filename=filename)
        
    full_results = optim.get_full_results(intersection)

    charts = Charts(portfolios=full_results, bench=bench, risk_free_rate=rfr, confidence_level=0.05)
    fig_1 = charts.viewer(portfolio_keys=None)
    fig_1.show()
    fig_2 = charts.cumulative_viewer(portfolio_keys=None)
    fig_2.show()
    print(charts.get_table()) # portfolio_keys=['R1_V1', 'R2_V1', 'R1_V2', 'R2_V2'])


def run_app(data:Data, K:int, n:int, m:int, ponderation_method:str, viewer:str, method:str=None) :
    """
    Executes the main application workflow for financial portfolio analysis, 
        which includes generating simple portfolios, applying selected weighting methods, intersecting portfolios, and producing visualizations of the results.

    :param data: An instance of the Data class, which provides access to necessary financial data and benchmark information.
    :param K: Integer specifying the rebalancing interval for the portfolios in months.
    :param n: Integer indicating the number of return-based portfolios to be generated.
    :param m: Integer indicating the number of volume-based portfolios to be generated.
    :param ponderation_method: String specifying the method to be used for weighting the portfolios. Supported methods are 'equi' for equal weighting, 'vol' for inverse volatility weighting, 'volume' for volume weighting, 'volumexprice' for dollar volume weighting, and 'best' for a presumably optimal but unspecified method.
    :param viewer: String specifying the type of visualization to be generated. Supported values are 'perf' for performance viewer, 'hist' for historical viewer, and 'cumulative_v' for cumulative viewer.
    :param method: Optional string specifying additional parameters or methods used specifically in the 'hist' viewer for historical data visualization.

    :return: matplotlib.figure.Figure object containing the generated plot, based on the specified viewer type.

    :raises ValueError: If an invalid ponderation method is specified, it throws a ValueError with an explanatory message.
    """
    bench = data.get_benchmark()
    signal = Signal(data=data, K=K, n_returns=n, m_volume=m)
    simple_returns, simple_volume = signal.create_simple_portfolios()
    
    optim = Optimisation(returns_portfolios=simple_returns, volume_portfolios=simple_volume)
    ponderation_methods = {"equi": optim.get_equal_weight,
                           "vol": optim.get_inverse_volatility_weight,
                           "volume": optim.get_volume_weight,
                           "volumexprice": optim.get_dollar_volume_weight, 
                            "best" :optim.get_best_weighting_method }

    if ponderation_method in ponderation_methods:
        weight_function = ponderation_methods[ponderation_method]
        weighted_returns = weight_function(simple_returns.copy())
        weighted_volume = weight_function(simple_volume.copy())
    else:
        raise ValueError(f"Invalid ponderation method: {ponderation_method}")
    intersection = signal.create_intersected_portfolios(returns_ptf=weighted_returns, volume_ptf=weighted_volume)
    full_results = optim.get_full_results(intersection)

    charts = Charts(portfolios=full_results, bench=bench)
    if viewer == "perf":
        fig = charts.viewer(portfolio_keys=None)
    elif viewer == "hist":
        fig = charts.get_figures(method, portfolio_keys=None)
    elif viewer == "cumulative_v":
        fig = charts.cumulative_viewer(portfolio_keys=None)
    
    return fig, charts.get_table()
