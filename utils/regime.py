import logging

import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# Frequency mappings
# pandas resample alias for each regime_interval label
_REPORT_FREQ: dict[str, str] = {
    'Daily':     'B',
    'Weekly':    'W-FRI',
    'Monthly':   'ME',
    'Quarterly': 'QE',
}

# Numeric order — used to detect when reporting is finer than data
_FREQ_ORDER: dict[str, int] = {
    '1d': 0,   'Daily': 0,
    '1wk': 1,  'Weekly': 1,
    '1mo': 2,  'Monthly': 2,
    '3mo': 3,  'Quarterly': 3,
}

# Number of data-cardinality steps that make up one reporting period
_STEPS_MAP: dict[str, dict[str, int]] = {
    '1d':  {'Daily': 1, 'Weekly': 5,  'Monthly': 21, 'Quarterly': 63},
    '1wk': {'Daily': 1, 'Weekly': 1,  'Monthly': 4,  'Quarterly': 13},
    '1mo': {'Daily': 1, 'Weekly': 1,  'Monthly': 1,  'Quarterly': 3},
    '3mo': {'Daily': 1, 'Weekly': 1,  'Monthly': 1,  'Quarterly': 1},
}

# Rolling window size in data-cardinality units (~2 years each)
_DEFAULT_WINDOW: dict[str, int] = {
    '1d':  504,
    '1wk': 104,
    '1mo': 60,
    '3mo': 20,
}

# How often to refit the HMM (in reporting periods)
_REFIT_EVERY: dict[str, int] = {
    'Daily':     21,   # once per calendar month
    'Weekly':    4,    # once per calendar month
    'Monthly':   1,
    'Quarterly': 1,
}

# Observation columns fed into GaussianHMM for each feature_set
_FEATURE_COLS: dict[str, list[str]] = {
    'returns': ['log_returns'],
    'macro':   ['log_returns', 'close_vix', 'close_hy', 'close_ten_yr',
                'close_inflation_fwd', 'close_fin_conditions'],
    'rvv':     ['log_returns', 'volume', 'log_vol'],
}

# Column index used to sort states (ascending = calm→stress)
# macro: VIX at index 1 → low VIX = regime 0 (calm)
# returns / rvv: log_returns at index 0 → low returns = regime 0 (bearish)
_SORT_COL: dict[str, int] = {
    'returns': 0,
    'macro':   1,
    'rvv':     0,
}


# Helpers
def _sort_states(model: hmm.GaussianHMM, col: int) -> None:
    """Re-order hidden states by ascending mean of `col` to prevent label switching."""
    order = np.argsort(model.means_[:, col])
    model.means_      = model.means_[order]
    model.covars_     = model.covars_[order]
    model.startprob_  = model.startprob_[order]
    model.transmat_   = model.transmat_[order][:, order]


def _rolling_regime_forecast(
    df: pd.DataFrame,
    data_cardinality: str,
    reporting_freq: str,
    feature_set: str,
    k_regimes: int,
    window_size: int,
    refit_every: int,
) -> pd.DataFrame | None:

    steps      = _STEPS_MAP[data_cardinality][reporting_freq]
    sort_col   = _SORT_COL.get(feature_set, 0)
    report_alias = _REPORT_FREQ[reporting_freq]

    # Warn when reporting is finer than data cardinality
    if _FREQ_ORDER[reporting_freq] < _FREQ_ORDER[data_cardinality]:
        logger.warning(
            f'Reporting ({reporting_freq}) is finer than data ({data_cardinality})'
            ' — regime labels will be forward-filled between observations.'
        )

    # Select available feature columns
    wanted = _FEATURE_COLS.get(feature_set, ['log_returns'])
    cols   = [c for c in wanted if c in df.columns]
    if not cols:
        logger.error(f'No feature columns found for feature_set="{feature_set}". '
                     f'Available: {df.columns.tolist()}')
        return None

    # Build date-indexed observation matrix
    X = df.set_index('date')[cols].copy()
    X.index = pd.to_datetime(X.index)

    # Reporting dates — last observation on or before each period boundary
    report_dates = X.resample(report_alias).last().dropna(how='all').index

    use_scaler = len(cols) > 1

    records: list[dict] = []
    model: hmm.GaussianHMM | None = None
    scaler: StandardScaler | None = None

    for i, report_date in enumerate(report_dates):
        window = X.loc[:report_date].iloc[-window_size:]

        # Burn-in guard: need at least half the window and enough rows per regime
        if len(window) < max(window_size // 2, k_regimes * 10):
            logger.debug(f'Skipping {report_date.date()} — insufficient rows ({len(window)})')
            continue

        # Refit on schedule
        if model is None or i % refit_every == 0:
            try:
                candidate = hmm.GaussianHMM(
                    n_components=k_regimes,
                    covariance_type='full',
                    n_iter=200,
                    tol=1e-4,
                    min_covar=1e-4,
                    random_state=42,
                )
                if use_scaler:
                    scaler = StandardScaler()
                    window_scaled = scaler.fit_transform(window.values)
                else:
                    window_scaled = window.values
                candidate.fit(window_scaled)
                _sort_states(candidate, col=sort_col)
                model = candidate
                logger.info(f'HMM refit at {report_date.date()}  window={len(window)}')
            except Exception as exc:
                logger.error(f'HMM fit failed at {report_date.date()}: {exc}')
                continue

        try:
            # At t=T, smoothed[-1] == filtered[-1] (no future observations)
            scaled = scaler.transform(window.values) if use_scaler else window.values
            filtered = model.predict_proba(scaled)[-1]

            # Forecast one reporting period ahead via transition matrix power
            forecast = filtered @ np.linalg.matrix_power(model.transmat_, steps)

            records.append({
                'date':            report_date,
                'current_regime':  int(np.argmax(filtered)),
                'forecast_regime': int(np.argmax(forecast)),
                'current_probs':   filtered.tolist(),
                'forecast_probs':  forecast.tolist(),
            })
        except Exception as exc:
            logger.error(f'Prediction failed at {report_date.date()}: {exc}')
            continue

    if not records:
        logger.warning('Rolling window produced no regime records.')
        return None

    result = pd.DataFrame(records).set_index('date')

    # Explode probability arrays into named columns
    cur_cols   = [f'p{i}_current'  for i in range(k_regimes)]
    fcast_cols = [f'p{i}_forecast' for i in range(k_regimes)]

    cur_df   = pd.DataFrame(result.pop('current_probs').tolist(),  index=result.index, columns=cur_cols)
    fcast_df = pd.DataFrame(result.pop('forecast_probs').tolist(), index=result.index, columns=fcast_cols)

    return pd.concat([result, cur_df, fcast_df], axis=1)