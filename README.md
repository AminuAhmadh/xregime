# Market Regime Classifier V2.0
### *Elite Macro Regime Detection — Powered by Free Data*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![yfinance](https://img.shields.io/badge/Data-yfinance-green)](https://pypi.org/project/yfinance/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Issues Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/YOUR_USERNAME/xregime/issues)

> **"Is the market in Risk-On, Risk-Off, or Mixed mode?"**  
> This system answers that question **daily**, using **12+ institutional-grade indicators** across **5 asset classes** — with **no API keys, no cost, no nonsense**.

---

## Live Output (Example – Oct 28, 2025)

============================================================
ANALYSIS COMPLETE - 2025-10-28 14:32:10
REGIME: RISK-ON
COMPOSITE SCORE: +0.612
CONFIDENCE: 82.4%

CATEGORY BREAKDOWN:
Equity               +0.73  ████████
Volatility           +0.65  ██████
Fixed_income         +0.30  ███
Currency             +0.48  █████
Commodity            -0.20  ██

INDICATOR DETAILS:
SPX_Trend            +1.00  ██████████
Sector_Rotation      +0.60  ██████
SmallCap_Strength    +0.40  ████
VIX                  +0.70  ███████
VIX_TermStructure    +0.60  ██████
CreditSpreads        +0.50  █████
Dollar_Strength      -0.60  ██████
JPY_Signal           +0.70  ███████
Risk_Currencies      +0.80  ████████
Gold_Signal          -0.20  ██
Treasury_10Y         +0.50  █████
YieldCurve           -0.20  ██
============================================================
TRADING IMPLICATIONS:

• Position Sizing: AGGRESSIVE (70-100%)
• Strategies: Breakout buying, momentum, growth
• Hedging: Minimal (10-15%)


---

## Features

| Feature | Description |
|-------|-----------|
| **12+ Indicators** | SPX trend, sector rotation, VIX, credit spreads, DXY, Gold, etc. |
| **5 Asset Classes** | Equities, Volatility, Fixed Income, FX, Commodities |
| **Composite Score** | Weighted, normalized `[-1, +1]` |
| **Confidence Metric** | Measures signal agreement |
| **Zero Cost** | Uses only **free `yfinance` data** |
| **Production Ready** | Full error handling, safe data parsing |
| **Actionable Output** | Direct trading implications |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/xregime.git
cd xregime

# 2. Install
pip install -r requirements.txt

# 3. Run
python regime.py

V2.1 Roadmap (Coming Soon)

Feature,Status,Notes
Streamlit Dashboard,Planned,Live web UI
Real Treasury Yields,Planned,"^TNX, ^FVX via yfinance"
Regime History Plot,Planned,6-month regime timeline
Email/Slack Alerts,Planned,Daily regime summary
Backtesting Module,Planned,Strategy PnL vs regime
CI/CD (GitHub Actions),Planned,Auto-run daily

How It Works

Fetches 180 days of data for 16 tickers
Calculates 12 indicators with robust fallbacks
Normalizes scores to [-1, 1]
Weights categories → Composite Score
Detects regime:

> +0.35 → RISK-ON
< -0.35 → RISK-OFF
Else → MIXED


Confidence = % of indicators agreeing

Indicators (Full List)

Indicator,Proxy For,Score Logic
SPX_Trend,Bull/Bear,% from 200MA
Sector_Rotation,Risk appetite,XLK/XLU ratio
SmallCap_Strength,Breadth,RUT vs SPX (21d)
VIX,Fear,Level + 5d change
VIX_TermStructure,Contango,VIX vs 50MA
CreditSpreads,Risk,HYG/LQD deviation
Dollar_Strength,Carry,DXY vs 50MA
JPY_Signal,Risk-off,USDJPY trend
Risk_Currencies,Risk-on,AUDUSD strength
Gold_Signal,Safe haven,Gold vs SPX
Treasury_10Y,Rates,(V2.1: real data)
YieldCurve,Recession,10Y-2Y (V2.1: real)

Contributing
PRs welcome! Especially:

Real yield curve (^TNX - ^IRX)
Dashboard (Streamlit)
Plotting (matplotlib/seaborn)
Backtesting

License
MIT License – Free to use, modify, and distribute.

Star this repo if you find it useful.