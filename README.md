# Market Regime Framework

A terminal-based GUI that fits a rolling-window **Gaussian Hidden Markov Model** to
market and macroeconomic data, producing probabilistic regime forecasts you can explore
in a notebook or apply to a machine learning model.

---
## Running the wizard
Run the main.py.

The wizard walks through **7 steps**. Navigate with arrow keys; press `Enter` to confirm,
`Q` to quit.

---

## Wizard walkthrough

### Step 1 — Asset Type

Choose whether you want to analyse an individual equity, an index / sector ETF, or a
commodity instrument.

```
   █████╗ ██╗     ██████╗  █████╗ ██╗  ██╗ █████╗
  ██╔══██╗██║     ██╔══██╗██╔══██╗╚██╗██╔╝██╔══██╗
  ███████║██║     ██████╔╝███████║ ╚███╔╝ ███████║
  ██╔══██║██║     ██╔═══╝ ██╔══██║ ██╔██╗ ██╔══██║
  ██║  ██║███████╗██║     ██║  ██║██╔╝ ██╗██║  ██║
  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
        M A R K E T   R E G I M E   F R A M E W O R K   v1.0

  Step 1 — Select Asset Type

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  ▶  Equity    Equity  (individual stock)                 │
  │     Index     Index / Sector ETF                         │
  │     Commodity Commodity                                  │
  │                                                          │
  │  Enter any listed equity ticker symbol on the            │
  │  next screen.                                            │
  └──────────────────────────────────────────────────────────┘

  [↑↓ Navigate]  [ENTER Select]  [Q Quit]
```

---

### Step 2 — Ticker

**Equity** — validated against Yahoo Finance:

```
  Step 2 — Enter Equity Ticker

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  Ticker symbol  ›  AAPL_                                 │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  [TYPE Enter value]  [ENTER Confirm]  [BKSP Delete]  [Q Quit if empty]
```

**Index / Sector ETF** — pre curated select menu:

```
  Step 2 — Select Index / Sector ETF

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  ▶  SPY    S&P 500 ETF                                   │
  │     QQQ    Nasdaq-100 ETF                                │
  │     DIA    Dow Jones ETF                                 │
  │     IWM    Russell 2000 ETF                              │
  │     NDX    Nasdaq ETF                                    │
  │     ─────────────────────────                            │
  │     XLF    Financials                                    │
  │     XLK    Technology                                    │
  │     XLE    Energy                                        │
  │     XLV    Health Care                                   │
  │     ...                                                  │
  └──────────────────────────────────────────────────────────┘
```

**Commodity** — pre curated select menu (GLD, SLV, USO, CPER).

---

### Step 3 — Date Range

Start and end dates entered separately in `YYYY/MM/DD` format:

```
  Step 3 — Enter Start Date

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  Start date  (YYYY/MM/DD)  ›  2000/01/01_                │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

---

### Step 4 — Data Cardinality

Sets the bar size used to fetch and fit the HMM.

```
  Step 4 — Select Data Cardinality

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │     Daily       1 bar per trading day                    │
  │     Weekly      1 bar per week                           │
  │  ▶  Monthly     1 bar per month                          │
  │     Quarterly   1 bar per quarter                        │
  │                                                          │
  │  1 bar per month                                         │
  └──────────────────────────────────────────────────────────┘
```

| Option | yfinance interval | Typical use |
|---|---|---|
| Daily | `1d` | Short-term signals, high granularity |
| Weekly | `1wk` | Medium-term trend |
| Monthly | `1mo` | Macro regime studies |
| Quarterly | `3mo` | Long-horizon allocation |

---

### Step 5 — HMM Feature Set

Determines which signals are fed as observations into the Gaussian HMM.

```
  Step 5 — Select HMM Feature Set

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │     Returns Only                                         │
  │     Returns + Volume + Volatility                        │
  │  ▶  Default — Returns + Macroeconomic                    │
  │                                                          │
  │  Bond yields, inflation data, etc.                       │
  └──────────────────────────────────────────────────────────┘
```

| Feature set | Columns fed to HMM |
|---|---|
| `returns` | `log_returns` |
| `rvv` | `log_returns`, `volume`, `log_vol` |
| `macro` | `log_returns`, VIX, HY spread, 10-yr yield, inflation fwd, fin. conditions |

---

### Step 6 — Regime Observation Interval

How often a regime label and probability vector is emitted. Independent of data
cardinality — the pipeline handles the mapping internally.

We recommed data cardinality of 'Daily', with a regime observation of a 'Monthly' interval.

```
  Step 6 — Select Regime Observation Interval

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │     Daily                                                │
  │     Weekly                                               │
  │  ▶  Monthly                                              │
  │     Quarterly                                            │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

> If reporting is finer than data cardinality (e.g. Daily reporting on Monthly data)
> regime labels are forward-filled between observations — a warning is logged.

---

### Step 7 — Output Path

Path where the results CSV will be saved. Defaults to `~/regime_<ticker>.csv`.

```
  Step 7 — Output File Path

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  Save path  ›  ~/regime_spy.csv_                         │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

---

### Confirmation screen

Review your full configuration before running. Use `← →` to choose
**Run Analysis** or **Go Back**.

```
  ┌──────────────────  Configuration Summary  ────────────────────┐
  │                                                               │
  │  Asset                   SPY                                  │
  │  Asset Type               Index                               │
  │  Start Date               2000/01/01                          │
  │  End Date                 2024/12/31                          │
  │  Data Cardinality         Monthly  ('1mo')                    │
  │  HMM Features             Default — Returns + Macroeconomic   │
  │  Regime Interval          Monthly                             │
  │  Output Path              ~/regime_spy.csv                    │
  │                                                               │
  └───────────────────────────────────────────────────────────────┘

         ✔  Run Analysis           ✗  Go Back

  [← → Choose]  [ENTER Confirm]  [Q Quit]
```

---

### Progress screen

The analysis runs in a background thread. The event log updates in real time;
scroll with `↑↓`. Press `Q` to close once complete.

```
  ┌────────────────────  Event Log  ──────────────────────────────┐
  │  ─────────────────────────────────────────────────────────    │
  │    Market Regime Analysis  ·  SPY                             │
  │  ─────────────────────────────────────────────────────────    │
  │    Asset type        Index                                    │
  │    Start date        2000/01/01                               │
  │    End date          2024/12/31                               │
  │    Data cardinality  Monthly  (yfinance: '1mo')               │
  │    Features          macro                                    │
  │    Obs. interval     Monthly                                  │
  │  ─────────────────────────────────────────────────────────    │
  │    [01/02]  Retrieving market & macro data…                   │
  │    ✓  Data retrieved  (299 rows)                              │
  │    [02/02]  Fitting rolling window HMM…                       │
  │    ✓  287 regime records computed                             │
  │    ✓  Saved → ~/regime_spy.csv                                │
  │  ─────────────────────────────────────────────────────────    │
  │    ✔  Analysis complete                                       │
  └───────────────────────────────────────────────────────────────┘

  ████████████████████████████████████████████████░  ✔  100%

  [↑↓ Scroll]  [Q Close]
```

---

## Output format

The results CSV has one row per reporting period:

| Column | Description |
|---|---|
| `date` | Period-end date (index) |
| `current_regime` | Most probable regime at period end (0 = bearish / calm, 2 = bullish / stressed — depends on feature set) |
| `forecast_regime` | Most probable regime one period ahead |
| `p0_current … p2_current` | Filtered state probabilities at period end |
| `p0_forecast … p2_forecast` | Forecast state probabilities one period ahead |

**Regime ordering**

| Feature set | Regime 0 | Regime 1 | Regime 2 |
|---|---|---|---|
| `returns` / `rvv` | Bearish (low returns) | Neutral | Bullish (high returns) |
| `macro` | Calm (low VIX) | Neutral | Stressed (high VIX) |

---

## Visualisation (notebook)

Load `notebooks/test.ipynb` and call `plot_regime_forecast` after running the wizard:

The chart renders two panels:
- **Top** — log-scale price with colour-coded regime shading
- **Bottom** — stacked forecast-probability area chart
