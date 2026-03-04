class RunTimeOptions:
    def __init__(self) -> None:
        self.indexes = [
            ("SPY",  "S&P 500 ETF"),
            ("QQQ",  "Nasdaq-100 ETF"),
            ("DIA",  "Dow Jones ETF"),
            ("IWM",  "Russell 2000 ETF"),
            ("NDX",  "Nasdaq ETF"),
        ]
        self.sector_etfs = [
            ("XLF",  "Financials"),
            ("XLK",  "Technology"),
            ("XLE",  "Energy"),
            ("XLV",  "Health Care"),
            ("XLI",  "Industrials"),
            ("XLC",  "Communication Services"),
            ("XLY",  "Consumer Discretionary"),
            ("XLP",  "Consumer Staples"),
            ("XLB",  "Materials"),
            ("XLRE", "Real Estate"),
            ("XLU",  "Utilities"),
        ]
        self.commodities = [
            ("GLD",  "Gold"),
            ("SLV",  "Silver"),
            ("USO",  "Crude Oil"),
            ("CPER", "Copper"),
        ]
        self.data_cardinalities = [
            ("1d",  "Daily",     "1 bar per trading day"),
            ("1wk", "Weekly",    "1 bar per week"),
            ("1mo", "Monthly",   "1 bar per month"),
            ("3mo", "Quarterly", "1 bar per quarter"),
        ]
        self.intervals = ["Daily", "Weekly", "Monthly", "Quarterly"]
        self.feature_sets = [
            ("returns", "Returns Only",
            "Uses only the asset's price returns as the HMM input feature."),
            ("rvv",     "Returns + Volume + Volatility",
            "Augments returns with the asset's own volume and realised volatility."),
            ("macro",   "Default — Returns + Macroeconomic",
            "Bond yields, inflation data, and gold/copper/oil ratios."),
        ]
        self.steps = [
            "Asset Type", "Ticker", "Date Range",
            "Data Cardinality", "Feature Set", "Regime Interval", "Output Path",
        ]
        self.HINT_NAV = [("↑↓", "Navigate"), ("ENTER", "Select"), ("Q", "Quit")]
        self.HINT_INPUT  = [("TYPE", "Enter value"), ("ENTER", "Confirm"),
               ("BKSP", "Delete"), ("Q", "Quit if empty")]
        self.HINT_CHOOSE = [("← →", "Choose"), ("ENTER", "Confirm"), ("Q", "Quit")]
        self.HINT_LOG    = [("↑↓", "Scroll"), ("Q", "Close")]





