import numpy as np
import pandas as pd
import yfinance as yf
import alpaxa_quant as aq
from config.api_keys import ApiKeys

ak = ApiKeys.from_env()

class DataRetrieval:
    def __init__(self):
        self.fred=ak.fred
        self.fred_base_url=ak.fred_base_url

    def get_historical_asset_data(self, ticker: str, start: str, end: str, cardinality: str) -> pd.DataFrame | None:
        raw = yf.download(tickers=ticker, start=start, end=end, interval=cardinality, auto_adjust=False)

        if raw.empty:
            return None

        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        raw = raw.reset_index()

        df = pd.DataFrame({
            'date':   raw['Date'],
            'open':   raw['Open'],
            'high':   raw['High'],
            'low':    raw['Low'],
            'close':  raw['Close'],
            'volume': raw['Volume'],
            'log_returns': np.log(raw['Close'] / raw['Close'].shift(1)),
            'log_vol': np.log(raw['Close'] / raw['Close'].shift(1)).rolling(window=4).std(),
        })

        df = df.dropna(axis=0)

        return df
    
    # Maps yfinance interval strings to pandas resample frequencies.
    # Daily maps to None (no resampling). fin_conditions is natively weekly so
    # it only gets resampled when the target is monthly or quarterly.
    _FREQ_MAP = {
        '1d':  None,
        '1wk': 'W-FRI',
        '1mo': 'ME',
        '3mo': 'QE',
    }

    def _resample(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        return df.resample(freq).mean()

    def get_macroeconmic_features(self, start:str, end:str, cardinality:str)-> (tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, 
                                                                     pd.DataFrame, pd.DataFrame] | None):
        fred=self.fred
        fred_base_url=self.fred_base_url

        try:
            vix = aq.fred.get_VIX(api_key=fred, base_url=fred_base_url, start_date=start, end_date=end) # d frequency
            hy = aq.fred.get_ICE_BofA_H_Y_option_adjusted_spread(api_key=fred, base_url=fred_base_url, start_date=start, end_date=end) # d frequency
            ten_yr = aq.fred.get_daily_ten_year_treasury_constant_maturity(api_key=fred, base_url=fred_base_url, start_date=start, end_date=end) # d frequency
            inflation_fwd = aq.fred.get_daily_five_yearly_forward_inflation_expectation_rate(api_key=fred, base_url=fred_base_url, start_date=start, end_date=end) # d frequency
            fin_conditions = aq.fred.get_fed_financial_conditions(api_key=fred, base_url=fred_base_url, start_date=start, end_date=end) # w frequency

            if vix.empty | hy.empty | ten_yr.empty | \
                inflation_fwd.empty | fin_conditions.empty:
                print('Empty df was returned.')
                return None

            freq = self._FREQ_MAP.get(cardinality)
            if freq is not None:
                # Resample daily series to target frequency using mean
                vix, hy, ten_yr, inflation_fwd = [
                    self._resample(df, freq)
                    for df in (vix, hy, ten_yr, inflation_fwd)
                ]
                # fin_conditions is weekly: resample to monthly/quarterly,
                # or align to the same weekly anchor when target is weekly
                fin_conditions = self._resample(fin_conditions, freq)

            return vix, hy, ten_yr, inflation_fwd, fin_conditions

        except Exception as e:
            print(e)
            return None
       

    def merge_technical_features(self, vix: pd.DataFrame, hy: pd.DataFrame, 
                                ten_yr: pd.DataFrame, inflation_fwd: pd.DataFrame,
                                fin_conditions: pd.DataFrame) -> pd.DataFrame | None:
        
        dfs  = [vix, hy, ten_yr, inflation_fwd, fin_conditions]
        cols = ['vix', 'hy', 'ten_yr', 'inflation_fwd', 'fin_conditions']

        dfs = [df.reset_index().rename(columns={'close': f'close_{col}'}) 
            for df, col in zip(dfs, cols)]

        result = dfs[0]
        for df in dfs[1:]:
            result = result.merge(df, on='date', how='left')


        result['close_fin_conditions'] = result['close_fin_conditions'].ffill()
        return result


    def flatten_multi_index(self, df: pd.DataFrame) -> pd.DataFrame | None:
        expected_columns = ['Close', 'High', 'Low', 'Open', 'Volume']

        if df.empty:
            print("Empty dataframe was passed")
            return None

        # Drop the ticker level from MultiIndex columns 
        df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        df_columns = df.columns.tolist()

        if not all(col in df_columns for col in expected_columns):
            print(f'Columns do not match. Got: {df_columns}')
            return None

        flattened_df = pd.DataFrame({
            'date': df['Date'],
            'open': df['Open'],
            'high': df['High'],
            'low': df['Low'],
            'close': df['Close'],
            'volume': df['Volume']
        })

        return flattened_df