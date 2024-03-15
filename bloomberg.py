import blpapi
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# A installer sur les ordi bloom : 
## python -m pip install --index-url=https://bcms.bloomberg.com/pip/simple blpapi

# Bloomberg names : 
DATE = blpapi.Name("date")
ERROR_INFO = blpapi.Name("errorInfo")
EVENT_TIME = blpapi.Name("EVENT_TIME")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
FIELD_ID = blpapi.Name("fieldId")
SECURITY = blpapi.Name("security")
SECURITY_DATA = blpapi.Name("securityData")

# Bloomberg data importation : 
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
            days = 'NON_TRADING_WEEKDAYS', fill = 'PREVIOUS_VALUE', curr = None):
        
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
            # msg = blpapi.event.MessageIterator(event).next() # -> ne fonctionne pas
            
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
        # request.set('date', snapshot_date.strftime('%Y%m%d'))
        # request.set('currency', curr)
        o = request.getElement('overrides').appendElement()
        o.setElement('value', snapshot_date)
        
                ############### Send request ###############

        requestID = self.session.sendRequest(request)
        print("Sending request")
        
                ############### Receive request ###############
        
        list_msg = []
        dict_Security_Fields = {}
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
        
                ############### Exploit data ###############
         
        for msg in list_msg:
            for sec_data in msg.getElement(SECURITY_DATA):  # Ticker
                ticker = sec_data.getElement(SECURITY).getValue()
                dict_Security_Fields = {}
                for field in sec_data.getElement(FIELD_DATA):  # Fields
                    dict_Security_Fields[field.name()] = field.getValue()
                list_pd.append(pd.DataFrame(dict_Security_Fields, index=[ticker]))

        return pd.concat(list_pd)
    
    
    def closeSession(self):
        print("Session closed")
        self.session.stop()
    
    
    
####################################################################################################################
################################################# Data importation #################################################
####################################################################################################################
     
# Cette partie pourras être mis dans le fichier data.py après les tests :)      
     
blp = BLP()

# Récupération des compo (bds): 
strFields = ["FIELD"] 
tickers = ["RIY Index"] # RUSSEL 
date = datetime(2024,2,28) # datetime(1999,1,28)
test_bds = blp.bds(strSecurity=tickers, strFields = strFields, snapshot_date = date) #, curr = "USD"

# Il faut faire une liste avec toute les dates et tourner avec une boucle for ? 
# Je sais pas si on peut tout prendre d'un coup ? 

# start_date = datetime(1999, 1, 28)
# end_date = datetime.now()

# dates_list = [start_date + i * timedelta(days=30) for i in range((end_date - start_date).days // 30 + 1)]

# df_compo = pd.DataFrame()
# for date in dates_list :
#     new_column = blp.bds(strSecurity=tickers, strFields = strFields, snapshot_date = date)
#     # nom colonne = date 
#     df_compo[date] = new_column [date]



    
# Récupération des fields (bdp): 
# tickers = ["GLE FP Equity", "FP FP Equity"] # récupéré la liste du bds 
# strFields = ["PX_LAST", "PX_VOLUME"] # +++ plein de truc 
# Start_date et end_date déjà créés en haut (pour la liste)
# test_bdh = blp.bdh(strSecurity=tickers, strFields = strFields, startdate = start_date, enddate = end_date, per='MONTHLY')

    
# Il faut renvoyer des dataframes comme ceux qu'on a commencé à utiliser 
    
blp.closeSession()
    
# PS : bdp fonctionne, bdh j'ai pas testé 
# PSS : bds a revoir 
    