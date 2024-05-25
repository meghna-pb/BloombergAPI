from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import blpapi
# A installer sur les ordi bloom : python -m pip install --index-url=https://bcms.bloomberg.com/pip/simple blpapi

# Bloomberg names : 
DATE = blpapi.Name("date")
ERROR_INFO = blpapi.Name("errorInfo")
EVENT_TIME = blpapi.Name("EVENT_TIME")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
FIELD_ID = blpapi.Name("fieldId")
SECURITY = blpapi.Name("security")
SECURITY_DATA = blpapi.Name("securityData")


class BLP():    
    
    def __init__(self):

        # Create Session object
        self.session = blpapi.Session()
        
        # Exit if can't start the Session
        if not self.session.start():
            print("Failed to start session.")
            return
        
        # Open & Get RefData Service or exit if impossible
        if not self.session.openService("//blp/refdata"):
            print("Failed to open //blp/refdata")
            return
        
        self.session.openService('//BLP/refdata')
        self.refDataSvc = self.session.getService('//BLP/refdata')

        print('Session open')
    
    #-----------------------------------------------------------------------------------------------------
    #------------------------------------------ BDH ------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------
    
    def bdh(self, strSecurity, strFields, startdate, enddate, per='DAILY', perAdj = 'CALENDAR', 
            days = 'NON_TRADING_WEEKDAYS', fill = 'PREVIOUS_VALUE', curr = "EUR"):
        
        """
            Summary:
                HistoricalDataRequest ; 
                Gets historical data for a set of securities and fields

            Inputs:
                strSecurity: list of str : list of tickers
                strFields: list of str : list of fields, must be static fields (e.g. px_last instead of last_price)
                startdate & enddate: dates
                per: periodicitySelection; daily, monthly, quarterly, semiannually or annually
                perAdj: periodicityAdjustment: ACTUAL, CALENDAR, FISCAL
                curr: string, else default currency is used 
                Days: nonTradingDayFillOption : NON_TRADING_WEEKDAYS*, ALL_CALENDAR_DAYS or ACTIVE_DAYS_ONLY
                fill: nonTradingDayFillMethod :  PREVIOUS_VALUE, NIL_VALUE
                Options can be selected these are outlined in “Reference Services and Schemas Guide.”    
            
            Output:
                A list containing as many dataframes as requested fields          
        """

                ############### Create request ###############
    
        request = self.refDataSvc.createRequest('HistoricalDataRequest')
        
        # Put field and securities in list if single value is passed
        if type(strFields) == str:
            strFields = [strFields]
        if type(strSecurity) == str:
            strSecurity = [strSecurity]
    
        # Set paramaters :
        for strF in strFields:
            request.append('fields', strF)
        for strS in strSecurity:
            request.append('securities', strS)
        request.set('startDate', startdate.strftime('%Y%m%d'))
        request.set('endDate', enddate.strftime('%Y%m%d'))
        request.set('periodicitySelection', per)
        request.set('periodicityAdjustment', perAdj)
        request.set('nonTradingDayFillOption', days)
        request.set('nonTradingDayFillMethod', fill)
        request.set('currency', curr)
    
                ############### Send request ###############
                
        requestID = self.session.sendRequest(request)
        print("Sending request")
        
                ############### Receive request ###############
        
        dict_Security_Fields = {}
        dict_tickers = {}
        list_msg = []
        
        for field in strFields:
            globals()['dict_'+ field]= {}
        
        while True:
            event = self.session.nextEvent()
            
            # Ignores anything that's not partial or final
            if (event.eventType() !=blpapi.event.Event.RESPONSE) & (event.eventType() !=blpapi.event.Event.PARTIAL_RESPONSE):
                continue      
                        
            # Extract the response message
            msg = blpapi.event.MessageIterator(event).__next__()
            
            # Fill message list
            list_msg.append(msg)
                   
            # Break loop if response is final
            if event.eventType() == blpapi.event.Event.RESPONSE:
                break        

                ############### Exploit data ###############
        
        for msg in list_msg:
            ticker = msg.getElement(SECURITY_DATA).getElement(SECURITY).getValue()
 
            # Create dict for each field
            for field in strFields:
                globals()['dict_'+ field][ticker] = {}
                
            for field_data in msg.getElement(SECURITY_DATA).getElement(FIELD_DATA):
                dat = field_data.getElement(0).getValue()
                
                for i in range(1, (field_data.numElements())):
                    field_name = str(field_data.getElement(i).name())
                    try:
                        globals()['dict_'+field_name][ticker][dat] = field_data.getElement(i).getValueAsFloat()
                    except:
                        globals()['dict_'+field_name][ticker][dat] = field_data.getElement(i).getValueAsString()
                        
            for field in strFields:
                dict_Security_Fields[field] = pd.DataFrame.from_dict(globals()['dict_'+ field], orient='columns')
                
        return dict_Security_Fields    
    
    #-----------------------------------------------------------------------------------------------------
    #------------------------------------------- BDP -----------------------------------------------------
    #-----------------------------------------------------------------------------------------------------
    
    def bdp(self, strSecurity, strFields, strOverrideField='', strOverrideValue=''):
        
        """
            Summary:
                Reference Data Request ; Real-time if entitled, else delayed values 
                Only supports 1 override
                
            Input:
                strSecurity (list of str) : list of tickers
                strFields (list of str) : list of fields, must be static fields (e.g. px_last instead of last_price)
                strOverrideField
                strOverrideValue         
            
            Output:
               Dict 
        """
        
                ############### Create request ###############

        request = self.refDataSvc.createRequest('ReferenceDataRequest')
        
        # Put field and securities in list is single field passed
        if type(strFields) == str:
            strFields = [strFields]
        if type(strSecurity) == str:
            strSecurity = [strSecurity]
            
        # Append list of fields & securities 
        for strD in strFields:
            request.append('fields', strD)
        for strS in strSecurity:
            request.append('securities', strS)

        # Add override 
        if strOverrideField != '':
            o = request.getElement('overrides').appendElement()
            o.setElement('fieldId', strOverrideField)
            o.setElement('value', strOverrideValue)

                ############### Send request ###############

        requestID = self.session.sendRequest(request)
        print("Sending request")
        
                ############### Receive request ###############             
                
        list_msg = []
        dict_Security_Fields = {}
        dict_tickers = {}
        list_pd = []
        
        while True:
            event = self.session.nextEvent()
            
            # Ignores anything that's not partial or final
            if (event.eventType() !=blpapi.event.Event.RESPONSE) & (event.eventType() !=blpapi.event.Event.PARTIAL_RESPONSE):
                continue
            
            # Extract the response message
            msg = blpapi.event.MessageIterator(event).__next__()
            
            # Fill message list
            list_msg.append(msg)
            
            # Break loop if response is final
            if event.eventType() == blpapi.event.Event.RESPONSE:
                break    

                ############### Extract the data ###############

        for msg in list_msg:
            for sec_data in msg.getElement(SECURITY_DATA): # Ticker
                ticker = sec_data.getElement(SECURITY).getValue()
                dict_Security_Fields = {}
                for field in sec_data.getElement(FIELD_DATA) : # Fields
                    dict_Security_Fields[field.name()] = field.getValue()
                dict_tickers[ticker] = pd.DataFrame.from_dict(dict_Security_Fields, orient='index')
                dict_tickers[ticker].columns = [ticker] 
                list_pd.append(dict_tickers[ticker].T)
        
        return pd.concat(list_pd)
    
    #-----------------------------------------------------------------------------------------------------
    #------------------------------------------- BDS -----------------------------------------------------
    #-----------------------------------------------------------------------------------------------------

    def bds(self, strSecurity, strFields, snapshot_date, curr=None):
        
        """
            Summary:
                Reference Data Request; retrieves snapshot data for a set of securities and fields for a specific date.

            Inputs:
                strSecurity: list of str: list of tickers
                strFields: list of str: list of fields, must be static fields (e.g., px_last instead of last_price)
                snapshot_date: date: the specific date for which you want the snapshot data
                curr: string, else default currency is used

            Output:
                A DataFrame containing snapshot data for the requested securities and fields at the specified date
        """
           
                ############### Create request ###############
    
        request = self.refDataSvc.createRequest('ReferenceDataRequest')
        
        # Put field and securities in list if single value is passed
        if type(strFields) == str:
            strFields = [strFields]
        if type(strSecurity) == str:
            strSecurity = [strSecurity]
    
        # Set paramaters :
        for strF in strFields:
            request.append('fields', strF)
        for strS in strSecurity:
            request.append('securities', strS)
        
        for strS in strSecurity:
            overrides = request.getElement('overrides')
            override = overrides.appendElement()
            override.setElement('fieldId', 'END_DT')
            override.setElement('value', snapshot_date.strftime('%Y%m%d'))
        
                ############### Send request ###############

        requestID = self.session.sendRequest(request)
        print("Sending request")
        
                ############### Receive request ###############
        
        list_msg = []
        dict_Security_Fields = {}
        list_compo = []
        field_name = strFields[0]
        
        while True:
            event = self.session.nextEvent()
            
            # Ignores anything that's not partial or final
            if (event.eventType() !=blpapi.event.Event.RESPONSE) & (event.eventType() !=blpapi.event.Event.PARTIAL_RESPONSE):
                continue
            
            # Extract the response message
            msg = blpapi.event.MessageIterator(event).__next__() 
            
            # Fill message list
            list_msg.append(msg)
            
            # Break loop if response is final
            if event.eventType() == blpapi.event.Event.RESPONSE:
                break        
        
                ############### Exploit data ###############
    
        for msg in list_msg:
            for sec_data in msg.getElement(SECURITY_DATA):  # Ticker
                ticker = sec_data.getElement(SECURITY).getValue()
                dict_Security_Fields = {}
                for member_data in sec_data.getElement(FIELD_DATA).getElement(field_name):
                    member = member_data.getElementAsString("Index Member") 
                    list_compo.append(member)
                dict_Security_Fields[ticker] = pd.DataFrame(list_compo, columns=[snapshot_date])
    
        return dict_Security_Fields
    
    def closeSession(self):
        print("Session closed")
        self.session.stop()


def fetch_bloomberg_data(start_date, end_date, index_ticker, data_fields = ["PX_LAST", "PX_VOLUME"]):
    """
    Fetches historical market data and index compositions from Bloomberg for specified tickers over a given date range.
    
    :param start_date (datetime): The beginning of the date range for data retrieval.
    :param end_date (datetime): The end of the date range for data retrieval.
    :param index_ticker (str): The Bloomberg ticker for the index whose data is to be fetched.
    :param data_fields (list of str): Specific fields of data to retrieve, default is last price and volume.

    :returns : A dictionary containing historical data for all unique constituents of the index
               and a DataFrame with index compositions on each date.
    """
    
    blp = BLP()

    # Generate a list of dates in monthly intervals
    dates_list = [start_date + i * timedelta(days=30) for i in range((end_date - start_date).days // 30 + 1)]
    
    strFields_compo = ["INDX_MWEIGHT_HIST"]  
    tickers = [index_ticker]
    df_compo = pd.DataFrame()

    for date in dates_list:
        # Fetch index compositions for each date
        results = blp.bds(strSecurity=tickers, strFields=strFields_compo, snapshot_date=date)
        new_column = results[tickers[0]]
        # Filter out entries where the column has digits
        new_column = new_column[~new_column[date].astype(str).apply(lambda x: any(char.isdigit() for char in x))]
        df_compo[date] = new_column[date]

    # Flatten tickers to get a unique list for all dates
    flattened_data = df_compo.values.ravel()
    flattened_data_unique = list(set(flattened_data))
    list_tickers = [str(ticker) + " Equity" for ticker in flattened_data_unique]

    # Fetch data for the tickers
    tickers = list_tickers
    dict_data = blp.bdh(strSecurity=tickers, strFields=data_fields, startdate=start_date, enddate=end_date, per='MONTHLY', curr="USD")
    blp.closeSession() 

    return dict_data, df_compo