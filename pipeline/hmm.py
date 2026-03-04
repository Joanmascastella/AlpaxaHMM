import logging
import pandas as pd
from config.regime import RegimeConfig

from utils.regime import _DEFAULT_WINDOW, _REFIT_EVERY, _rolling_regime_forecast

logger = logging.getLogger(__name__)

class HMMPipeline:
    def run(
        self,
        data: pd.DataFrame,
        config: RegimeConfig,
        k_regimes: int = 3,
        window_size: int | None = None,
        refit_every: int | None = None,
    ) -> pd.DataFrame | None:

        cardinality   = config.data_cardinality
        reporting     = config.regime_interval
        feature_set   = config.feature_set

        window_size = window_size or _DEFAULT_WINDOW.get(cardinality, 252)
        refit_every = refit_every or _REFIT_EVERY.get(reporting, 1)

        logger.info(
            f'HMM pipeline — cardinality={cardinality}  '
            f'reporting={reporting}  features={feature_set}  '
            f'k={k_regimes}  window={window_size}  refit_every={refit_every}'
        )

        return _rolling_regime_forecast(
            df               = data,
            data_cardinality = cardinality,
            reporting_freq   = reporting,
            feature_set      = feature_set,
            k_regimes        = k_regimes,
            window_size      = window_size,
            refit_every      = refit_every,
        )
