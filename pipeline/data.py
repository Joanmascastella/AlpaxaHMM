import logging
from typing import Any
import pandas as pd
from config.regime import RegimeConfig
from utils.validators import RunTimeUtils 
from utils.data_retrieval import DataRetrieval

# Constants
rtu = RunTimeUtils()
dt  = DataRetrieval()

# Set up logger
logging.basicConfig(
    filename='.logs/data_retrieval.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',

)
logger = logging.getLogger(__name__)

class Data:
    def __init__(self):
        pass

    def run(self, config: RegimeConfig)-> pd.DataFrame | None:
        # log 
        logger.info(config)
        
        # Retrieve fields from config
        asset_type = config.asset_type
        ticker = config.ticker
        start_date = config.start_date.replace('/', '-')
        end_date = config.end_date.replace('/', '-')
        data_cardinality = config.data_cardinality
        feature_set = config.feature_set

        # Check the asset type
        if asset_type == 'equity':
             # Check that ticker exsits
             exists = rtu.ticker_exists(ticker=ticker)
             if exists:
                df = self._get_data(ticker=ticker, start_date=start_date, end_date=end_date, 
                                    cardinality=data_cardinality, feature_set=feature_set)
                
                # If empty return none
                if df is None or df.empty:
                     logger.warning(f'Dataframe was empty')
                     return None
                
                return df
             # If the equity ticker does not exists then return None
             else:
                  logger.warning(f'Ticker does not exists: {ticker}')
                  return None
    
        # Loop for commodity and sector etfs or indexes    
        else:
             converted_ticker = self._map_to_yfinance(ticker=ticker)
             df = self._get_data(ticker=converted_ticker, start_date=start_date, end_date=end_date,
                                 cardinality=data_cardinality, feature_set=feature_set)
             
             #If empty return None
             if df is None or df.empty:
                  logger.warning('Dataframe was empty')
                  return None
        

             return df

    def _map_to_yfinance(self, ticker:str)->str:
        ticker_map = [
            ("SPY",  "^GSPC"),
            ("QQQ",  "QQQ"),
            ("DIA",  "^DJI"),
            ("IWM",  "IWN"),
            ("NDX",  "^IXIC"),
            ("XLF",  "XLF"),
            ("XLK",  "XLK"),
            ("XLE",  "XLE"),
            ("XLV",  "XLV"),
            ("XLI",  "XLI"),
            ("XLC",  "XLC"),
            ("XLY",  "XLY"),
            ("XLP",  "XLP"),
            ("XLB",  "XLB"),
            ("XLRE", "XLRE"),
            ("XLU",  "XLU"),
            ("GLD",  "GC=F"),
            ("SLV",  "SI=F"),
            ("USO",  "CL=F"),
            ("CPER", "HG=F")
        ]        

        ticker_map_dict = dict(ticker_map)
        converted_ticker = ticker_map_dict[ticker]  
        return converted_ticker

    def _get_data(self, ticker: str, start_date: str, end_date: str, 
                  cardinality: str, feature_set: int) ->  (tuple[pd.DataFrame | None, pd.DataFrame | None] | pd.DataFrame | Any | None):
            try:
                # Get historical data
                historical_asset_data = dt.get_historical_asset_data(ticker=ticker, start=start_date, 
                                            end=end_date, cardinality= cardinality)
                
                # Return only asset returns
                if feature_set == 'returns':
                    allowed_cols = ['date', 'log_returns']
                    returns = historical_asset_data[allowed_cols]
                    return returns
                
                # Return asset returns + macro
                if feature_set == 'macro':
                    macro = dt.get_macroeconmic_features(start=start_date, end=end_date, cardinality=cardinality)
                    if macro is None:
                        return None
                    vix, hy, ten_yr, inflation_fwd, fin_conditions = macro

                    merged_technicals = dt.merge_technical_features(vix=vix, hy=hy, ten_yr=ten_yr, 
                                                inflation_fwd=inflation_fwd, fin_conditions=fin_conditions)
                    
                    master_df = pd.merge(
                         left=historical_asset_data[['date', 'log_returns']],
                         right=merged_technicals,
                         on='date',
                         how='left'
                    )
                    master_df = master_df.dropna()

                    return master_df

                # Return asset returns, volume and volatility
                if feature_set == 'rvv':
                    allowed_cols = ['date', 'volume', 'log_vol', 'log_returns']
                    rvv = historical_asset_data[allowed_cols]
                    return rvv 
        
            except Exception as e:
                 print(e)
                 return
                
                    