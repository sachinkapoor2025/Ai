import os
import tpqoa
from datetime import datetime

from livetrading.BollingerBandsLive import BollingerBandsLive
from livetrading.ContrarianLive import ContrarianLive
from livetrading.MLClassificationLive import MLClassificationLive
from livetrading.MomentumLive import MomentumLive
from livetrading.SMALive import SMALive

from backtesting.ContrarianBacktest import ContrarianBacktest
from backtesting.BollingerBandsBacktest import BollingerBandsBacktest
from backtesting.MomentumBacktest import MomentumBacktest
from backtesting.SMABacktest import SMABacktest
from backtesting.MLClassificationBacktest import MLClassificationBacktest

def lambda_handler(event, context):
    """ AWS Lambda-compatible entry point """

    # Step 1: Ensure OANDA Configuration File
    cfg = "oanda.cfg"
    
    # Step 2: Open OANDA Connection
    oanda = tpqoa.tpqoa(cfg)

    # Step 3: Choose Instrument from ENV
    instrument = os.getenv("TRADE_INSTRUMENT", "EUR_USD")
    available_instruments = [inst[1] for inst in oanda.get_instruments()]
    
    if instrument not in available_instruments:
        instrument = "EUR_USD"  # Default if invalid instrument is provided
    
    print(f"Instrument Selected: {instrument}")

    # Step 4: Trading Mode Selection
    mode = os.getenv("TRADING_MODE", "1")  # "1" = Live, "2" = Backtest

    if mode not in ["1", "2"]:
        mode = "1"  # Default to Live Trading

    # Step 5: Select Strategy
    if mode == "1":  # Live Trading
        strategy = os.getenv("STRATEGY", "sma").lower()
        available_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification"]

        if strategy not in available_strategies:
            strategy = "sma"  # Default to SMA Strategy
        
        granularity = os.getenv("GRANULARITY", "1hr")
        units = int(os.getenv("UNITS", "100000"))
        stop_profit = os.getenv("STOP_PROFIT", "0")
        stop_loss = os.getenv("STOP_LOSS", "0")

        # Convert stop values to float or None
        stop_profit = None if stop_profit == "n" else float(stop_profit)
        stop_loss = None if stop_loss == "n" else float(stop_loss)

        # Initialize Trading Strategy
        if strategy == "sma":
            smas = int(os.getenv("SMAS", "9"))
            smal = int(os.getenv("SMAL", "20"))
            trader = SMALive(cfg, instrument, granularity, smas, smal, units, stop_loss=stop_loss, stop_profit=stop_profit)

        elif strategy == "bollinger_bands":
            sma = int(os.getenv("SMA", "9"))
            deviation = int(os.getenv("DEVIATION", "2"))
            trader = BollingerBandsLive(cfg, instrument, granularity, sma, deviation, units, stop_loss=stop_loss, stop_profit=stop_profit)

        elif strategy == "momentum":
            window = int(os.getenv("WINDOW", "3"))
            trader = MomentumLive(cfg, instrument, granularity, window, units, stop_loss=stop_loss, stop_profit=stop_profit)

        elif strategy == "contrarian":
            window = int(os.getenv("WINDOW", "3"))
            trader = ContrarianLive(cfg, instrument, granularity, window, units, stop_loss=stop_loss, stop_profit=stop_profit)

        elif strategy == "ml_classification":
            lags = int(os.getenv("LAGS", "6"))
            trader = MLClassificationLive(cfg, instrument, granularity, lags, units, stop_loss=stop_loss, stop_profit=stop_profit)

        print(f"Live Trading Started with {strategy} strategy on {instrument}")

    else:  # Backtesting
        strategy = os.getenv("STRATEGY", "sma").lower()
        available_backtest_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification"]

        if strategy not in available_backtest_strategies:
            strategy = "sma"  # Default to SMA

        start_date = os.getenv("START_DATE", "2024-01-01")
        end_date = os.getenv("END_DATE", "2024-12-31")
        trading_cost = float(os.getenv("TRADING_COST", "0.00007"))
        granularity = os.getenv("GRANULARITY", "H1")

        if strategy == "sma":
            smas = int(os.getenv("SMAS", "9"))
            smal = int(os.getenv("SMAL", "20"))
            trader = SMABacktest(instrument, start_date, end_date, smas, smal, granularity, trading_cost)

        elif strategy == "bollinger_bands":
            sma = int(os.getenv("SMA", "9"))
            deviation = int(os.getenv("DEVIATION", "2"))
            trader = BollingerBandsBacktest(instrument, start_date, end_date, sma, deviation, granularity, trading_cost)

        elif strategy == "momentum":
            window = int(os.getenv("WINDOW", "3"))
            trader = MomentumBacktest(instrument, start_date, end_date, window, granularity, trading_cost)

        elif strategy == "contrarian":
            window = int(os.getenv("WINDOW", "3"))
            trader = ContrarianBacktest(instrument, start_date, end_date, window, granularity, trading_cost)

        elif strategy == "ml_classification":
            trader = MLClassificationBacktest(instrument, start_date, end_date, granularity, trading_cost)

        print(f"Backtesting Started with {strategy} strategy on {instrument}")

    return {"status": "Success", "mode": mode, "strategy": strategy, "instrument": instrument}
