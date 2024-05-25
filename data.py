import pandas as pd
from datetime import datetime
import pandas as pd
import os
from datetime import datetime as dt
from glob import glob
import pyarrow.parquet as pq

VOLUME, PX_LAST, RETURNS, VOLATILITY, RFR, WEIGHT, WEIGHTED_RETURNS = "PX_VOLUME", "PX_LAST", "RETURNS", "VOLATILITY", "RFR", "WEIGHT", "WEIGHTED_RETURNS"
parquetTempFilePath = "Data/parquet/"

class Data:
    def __init__(self, path="", J=3, risk_free_rate:float=0.2, index_ticker = 'RIY Index', 
                 start_date = datetime(2024, 1, 28), end_date = datetime.now()) -> None:
        """
        Initialize the Data class with the option to load data from a specified path or use predefined Bloomberg data.
        
        :param path: Path to the Excel files containing the data. If empty, uses predefined Bloomberg data.
        :param J: Number of periods used for calculating rolling statistics such as volatility and expected returns.
        :param risk_free_rate: The risk-free rate used in financial calculations.
        """

        self.J = J  
        self.risk_free_rate = risk_free_rate
        
        if path == "":
            from bloomberg import fetch_bloomberg_data
            dict_data, df_compo = fetch_bloomberg_data(start_date, end_date, index_ticker)
            self.df_compo = df_compo
            self.df_px_last = dict_data[PX_LAST].sort_index()
            self.df_px_volume = dict_data[VOLUME].sort_index()
        else:
            self.df_compo = self.__read_file('Data/Bloomberg_Compo.xlsx', sheet_name="Compo")
            self.df_px_last = self.__read_file('Data/Bloomberg_Data.xlsx', sheet_name='PX LAST', saveToParquet=True, index_col=0)
            self.df_px_volume = self.__read_file('Data/Bloomberg_Data.xlsx', sheet_name='PX VOLUME', saveToParquet=True, index_col=0)
        
        self.df_px_last = self.__treat_df(self.df_px_last, format='%Y%m%d')
        self.df_px_volume = self.__treat_df(self.df_px_volume, format='%Y%m%d')
        self.df_compo.columns = pd.to_datetime(self.df_compo.columns, format='%Y%m%d')
        self.df_returns = self.__calculate_returns()
        self.df_volatility = self.__calculate_volatility()
        
        
    def __treat_df(self, df, format) -> pd.DataFrame:
        """
        Cleans DataFrame columns, including stripping of extra characters and standardizing date formats.
        
        :param df: DataFrame to be treated.
        :param format: String format to parse the index as dates.
        """
        df.columns = df.columns.str.replace(" Equity", "")
        df.index = pd.to_datetime(df.index, format=format)
        return df.sort_index()
    
    def convertToFloatOrStr(self, val):
        """
        Attempts to convert the input value to a float. 
        If the conversion fails due to a ValueError, it converts the value to a string instead.

        :param val: The value to be converted. This can be any type that is convertible to float or string.
        :return: The converted value, either as a float if convertible, otherwise as a string.
        """
        try:
            return float(val)
        except ValueError:
            return str(val)
        
    def __read_file(self, filepath, sheet_name=None, saveToParquet=True, index_col=None):
        """
        Reads data from the specified file path. 

        :param filepath: String specifying the path to the file that needs to be read.
        :param sheet_name: Optional string specifying the Excel sheet name to be read. If None, the default sheet is read.
        :param saveToParquet: Boolean indicating whether to save the read data to a Parquet file for quicker subsequent reads.
        :param index_col: Optional parameter to specify the column to be used as the index in the DataFrame.

        :return: A pandas DataFrame containing the data read from the file.

        :raises FileNotFoundError: If the specified file does not exist at the given filepath.
        """
        
        if filepath.endswith(".parquet"):
            return pd.read_parquet(filepath)
        
        DATA = pd.DataFrame()

        # Reads a file, receives an xlsx file. Tests to find if the parquet file exists.
        # if it doesn't, it reads the excel and creates parquet, if it does, it reads the parquet
        directory, filename = os.path.split(filepath)
        modification_time = os.path.getmtime(filepath)
        parquetFileName = filename[:-5].replace(' ', '_') + str(int(modification_time))
        if sheet_name:
            parquetFileName += "_" + sheet_name
        parquetFileName += ".parquet"
        parquetFilePath = os.path.join(parquetTempFilePath, parquetFileName)
        
        if os.path.exists(parquetFilePath):
            DATA = pd.read_parquet(parquetFilePath)
            for col in DATA.columns:
                try:
                    DATA[col] = DATA[col].astype(float)
                except:
                    DATA[col] = DATA[col].apply(self.convertToFloatOrStr)
        else:
            try:
                FILE = pd.ExcelFile(filepath) #, engine="openpyxl")
                if sheet_name:
                    DATA = pd.read_excel(FILE, sheet_name, index_col=index_col)
                else:
                    DATA = pd.read_excel(filepath, index_col=index_col)
            except FileNotFoundError:
                raise FileNotFoundError("\n\nThe file '"+filename+"' was not found in the directory '"+directory+"'.")
            
            if len(DATA) > 0 and saveToParquet:
                DATA.astype(str).to_parquet(parquetFilePath, engine='pyarrow')
        
        return DATA

    def __calculate_returns(self) -> pd.DataFrame:
        """
        Calculates the percentage change in PX_LAST to derive returns, applied on a forward-filled DataFrame.
        """
        return self.df_px_last.apply(lambda colonne: colonne.ffill().pct_change(fill_method=None).dropna())
    
    def __calculate_volatility(self) -> pd.DataFrame:
        """
        Calculates rolling volatility over the specified window J and handles any resulting NA values.
        """
        df_volatility = self.df_returns.rolling(window=self.J).std()
        df_volatility.replace(0, pd.NA, inplace=True)
        df_volatility = df_volatility.fillna(method='ffill').fillna(method='bfill')
        return df_volatility

    def get_data(self, K:int=1) -> dict:
        """
        Aggregates and aligns all financial data by rebalancing date intervals, tailored for portfolio construction.
        
        :param K: Frequency of rebalance in months.
        """
        data = {}
        valid_index = self.df_px_last.index[self.J]  # +1
        rebalance_dates = pd.date_range(valid_index, self.df_px_last.index[-1], freq=f'{K}ME')

        for date in rebalance_dates :
            if date in self.df_px_last.index:
                nearest_date = min(pd.to_datetime(self.df_compo.columns), key=lambda x: abs(x - pd.to_datetime(date)))            
                px_last = self.df_px_last.loc[[date]].rename(index={date: nearest_date})
                px_volume = self.df_px_volume.loc[[date]].rename(index={date: nearest_date})
                returns = self.df_returns.loc[[date]].rename(index={date: nearest_date})
                volatility = self.df_volatility.loc[[date]].rename(index={date: nearest_date})

                tickers = self.df_compo[nearest_date].dropna().tolist()
                data[nearest_date] = pd.concat([px_last.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: PX_LAST}), 
                                            px_volume.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLUME}), 
                                            returns.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: RETURNS}),
                                            volatility.reindex(tickers, axis='columns').dropna(axis=1).rename(index={nearest_date: VOLATILITY})]).T
        return data

    def get_benchmark(self):
        results = []
        for date in self.df_returns.index:
            nearest_date = min(pd.to_datetime(self.df_compo.columns), key=lambda x: abs(x - pd.to_datetime(date)))
            tickers = self.df_compo[nearest_date].dropna().tolist()
            returns = self.df_returns.loc[date].reindex(tickers).dropna()
            if tickers:
                equal_weight = 1 / len(tickers)
            else:
                equal_weight = 0
            weighted_returns = (returns * equal_weight).sum()

            results.append([nearest_date, weighted_returns])
        results_df = pd.DataFrame(results, columns=['DATES', 'WEIGHTED_RETURNS'])

        results_df.set_index('DATES', inplace=True)
        
        return results_df

