import os
import boto3
import tpqoa
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from decimal import Decimal  # ✅ Import Decimal for DynamoDB compatibility
import talib  # ✅ Technical Indicators Library

# Initialize AWS Clients
dynamodb = boto3.client('dynamodb')
dynamodb_resource = boto3.resource('dynamodb')

def check_or_create_table(currency_pair):
    """ Check if the table exists, and create it if it doesn't. """
    table_name = f"fx-trading-{currency_pair}"
    try:
        # Check if table exists
        dynamodb.describe_table(TableName=table_name)
        print(f"[INFO] Table {table_name} already exists.")
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"[INFO] Table {table_name} does not exist. Creating it now...")

        # Create the table
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "TradeID", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "TradeID", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )

        # Wait until the table is fully created before proceeding
        while True:
            response = dynamodb.describe_table(TableName=table_name)
            table_status = response["Table"]["TableStatus"]
            if table_status == "ACTIVE":
                print(f"[INFO] Table {table_name} is now ACTIVE and ready for writes.")
                break
            print(f"[INFO] Waiting for table {table_name} to become ACTIVE...")
            time.sleep(2)

def convert_floats_to_decimal(data):
    """ Recursively converts all float values to Decimal (DynamoDB Requirement). """
    if isinstance(data, float):
        return Decimal(str(data))  # Convert float to string first to avoid precision issues
    elif isinstance(data, dict):
        return {k: convert_floats_to_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimal(i) for i in data]
    else:
        return data

def fetch_market_data(oanda, instrument, granularity="M1", count=100):
    """ Fetch historical market data from OANDA for the given instrument. """
    print(f"[INFO] Fetching market data for {instrument}...")
    data = oanda.get_history(instrument=instrument, granularity=granularity, count=count)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df.set_index("time", inplace=True)
    return df

def calculate_technical_indicators(df):
    """ Calculate key technical indicators and return as a dictionary. """
    print("[INFO] Calculating technical indicators...")

    # Convert prices to numpy arrays for TA-Lib calculations
    df["close"] = df["closeMid"].astype(float)
    df["high"] = df["highMid"].astype(float)
    df["low"] = df["lowMid"].astype(float)
    df["open"] = df["openMid"].astype(float)

    indicators = {}

    # Moving Averages
    indicators["SMA_20"] = talib.SMA(df["close"], timeperiod=20)[-1]
    indicators["SMA_50"] = talib.SMA(df["close"], timeperiod=50)[-1]
    indicators["EMA_20"] = talib.EMA(df["close"], timeperiod=20)[-1]

    # RSI (Relative Strength Index)
    indicators["RSI_14"] = talib.RSI(df["close"], timeperiod=14)[-1]

    # MACD (Moving Average Convergence Divergence)
    macd, macdsignal, macdhist = talib.MACD(df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
    indicators["MACD"] = macd[-1]
    indicators["MACD_Signal"] = macdsignal[-1]

    # Bollinger Bands
    upper, middle, lower = talib.BBANDS(df["close"], timeperiod=20)
    indicators["BB_Upper"] = upper[-1]
    indicators["BB_Lower"] = lower[-1]

    return indicators

def write_trade_log(trade_id, currency_pair, trade_data):
    """ Write trade logs to the corresponding DynamoDB table. """
    table_name = f"fx-trading-{currency_pair}"
    check_or_create_table(currency_pair)  # Ensure the table exists

    table = dynamodb_resource.Table(table_name)

    trade_data["TradeID"] = trade_id
    trade_data["Timestamp"] = int(datetime.utcnow().timestamp())

    # ✅ Convert float values to Decimal
    trade_data = convert_floats_to_decimal(trade_data)

    # ✅ Wait for table status to be "ACTIVE" before writing data
    while True:
        response = dynamodb.describe_table(TableName=table_name)
        table_status = response["Table"]["TableStatus"]
        if table_status == "ACTIVE":
            break
        print(f"[INFO] Waiting for table {table_name} to be ready for writing...")
        time.sleep(2)

    table.put_item(Item=trade_data)
    print(f"[INFO] Trade log written to {table_name}: {trade_data}")

def lambda_handler(event, context):
    """ AWS Lambda-compatible entry point """
    try:
        print("[INFO] Lambda function started.")

        # Step 1: Ensure OANDA Configuration File
        cfg = "oanda.cfg"
        print(f"[INFO] Using OANDA config file: {cfg}")

        # Step 2: Open OANDA Connection
        oanda = tpqoa.tpqoa(cfg)
        print("[INFO] OANDA connection established.")

        # Step 3: Fetch All Available Instruments (Currency Pairs)
        available_instruments = [inst[1] for inst in oanda.get_instruments()]
        print(f"[INFO] Available Instruments: {available_instruments}")

        # Step 4: Iterate Through All Available Currency Pairs and Store Data
        for instrument in available_instruments:
            print(f"[INFO] Processing trade log for {instrument}...")

            # Fetch market data and calculate indicators
            df = fetch_market_data(oanda, instrument)
            indicators = calculate_technical_indicators(df)

            trade_data = {
                "Instrument": instrument,
                "Granularity": "M1",
                "SMA_20": indicators["SMA_20"],
                "SMA_50": indicators["SMA_50"],
                "EMA_20": indicators["EMA_20"],
                "RSI_14": indicators["RSI_14"],
                "MACD": indicators["MACD"],
                "MACD_Signal": indicators["MACD_Signal"],
                "BB_Upper": indicators["BB_Upper"],
                "BB_Lower": indicators["BB_Lower"]
            }

            # Write trade log to DynamoDB
            write_trade_log(trade_id=f"T{int(datetime.utcnow().timestamp())}", currency_pair=instrument, trade_data=trade_data)

        print("[INFO] Lambda function execution completed successfully.")
        return {"status": "Success", "processed_currency_pairs": available_instruments}

    except Exception as e:
        print(f"[ERROR] Lambda function failed: {str(e)}")
        return {"status": "Failed", "error": str(e)}
