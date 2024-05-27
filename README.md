# BloombergAPI
Implementation of a quantitative Long-Short strategy, based on the paper "Price Momentum and Trading Volume"

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Modules](#modules)
  - [data.py](#datapy)
  - [main.py](#mainpy)
  - [optimisation.py](#optimisationpy)
  - [performance.py](#performancepy)
  - [signals.py](#signalspy)
  - [tools.py](#toolspy)
  - [app.py](#apppy)
  - [bloomberg.py](#bloombergpy)
  - [charts.py](#chartspy)

## Installation

To install the necessary dependencies for this project, run the following command:

```bash
pip install -r requirements.txt
```

## Usage
To open the streamlit app, run the following command:
```bash
streamlit run app.py
```
The app will open in a browser page. You can then select the index; if it's RIY Index, you can use the data from Excel or Bloomberg, otherwise it will fetch the info from Bloomberg. 
If you fetch the information from Bloomberg, be mindful that it takes very long to run the code on the dates we have. 
You can also choose the number of returns and volume portfolios, the holding period and the period of returns, the risk-free rate.
Finally, you can choose the weighting-scheme, and the graph you want to see.

### Example
To run the `main.py` file :
```bash
python main.py
```

Here is how the `main.py` works : 
```python
# first, we declare the parameters
nb_periods = 3
rebalancing_interval = 6
nb_returns_based_ptf = 10
nb_volume_based_ptf = 5
risk_free_rate = 0.2
ponderation_method = "equi"
file_name = "inputs_port"

# then, we use the "run_excel" function (it will source itself from our Excel extract )
run_excel(J = nb_periods, 
          K = rebalancing_interval, 
          n = nb_returns_based_ptf, 
          m = nb_volume_based_ptf, 
          risk_free_rate = risk_free_rate, 
          ponderation_method = ponderation_method) 
```
The main is mostly used for testing, if we want to change the parameters etc. But to call the Bloomberg API, we use the `app.py`

## Modules
### bloomberg.py
Handles data fetching from the Bloomberg API. It provides methods to retrieve financial data from Bloomberg's services and process it for further analysis.

### data.py
Contains the `Data` class for loading and processing financial data. It handles fetching data from different sources (either Excel or Bloomberg) and performs initial data transformations.

### optimisation.py
Includes the `Optimisation` class for optimising portfolio weights and implementing different financial optimisation strategies. It handles the adjustment of parameters to maximise portfolio performance.

### performance.py
Contains the `Performance` class for evaluating financial models and strategies. It provides methods to calculate various performance metrics, such as the Sharpe Ratio, Value at Risk, and tracking error.

### signals.py
Includes the `Signal` class for analyzing financial signals. It processes raw data to identify trading signals and trends, facilitating informed decision-making.

### tools.py
Provides utility functions used across different modules in the project. This includes helper functions for exporting our portfolios for PORT, running the app, or running our strategies from the Excel sheet.

### charts.py
Includes the `Charts` class for creating visualisations of the data and analysis results. It generates various plots to represent portfolio performance metrics and other key insights.
