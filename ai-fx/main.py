import os
import boto3
import tpqoa
from datetime import datetime
import time

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
        
        # Wait until table is created
        while True:
            try:
                dynamodb.describe_table(TableName=table_name)
                print(f"[INFO] Table {table_name} successfully created.")
                break
            except dynamodb.exceptions.ResourceNotFoundException:
                time.sleep(2)

def write_trade_log(trade_id, currency_pair, trade_data):
    """ Write trade logs to the corresponding DynamoDB table. """
    table_name = f"fx-trading-{currency_pair}"
    check_or_create_table(currency_pair)  # Ensure the table exists
    
    table = dynamodb_resource.Table(table_name)
    trade_data["TradeID"] = trade_id
    trade_data["Timestamp"] = int(datetime.utcnow().timestamp())

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

        # Step 3: Choose Instrument
        instrument = os.getenv("TRADE_INSTRUMENT", "EUR_USD")
        available_instruments = [inst[1] for inst in oanda.get_instruments()]
        
        if instrument not in available_instruments:
            print(f"[WARNING] Invalid instrument selected: {instrument}. Defaulting to EUR_USD.")
            instrument = "EUR_USD"

        print(f"[INFO] Instrument Selected: {instrument}")

        # Step 4: Trading Mode Selection
        mode = os.getenv("TRADING_MODE", "1")  # "1" = Live, "2" = Backtest
        if mode not in ["1", "2"]:
            print(f"[WARNING] Invalid mode selected: {mode}. Defaulting to Live Trading.")
            mode = "1"

        print(f"[INFO] Trading Mode: {'Live' if mode == '1' else 'Backtesting'}")

        # Step 5: Select Strategy
        strategy = os.getenv("STRATEGY", "sma").lower()
        available_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification"]

        if strategy not in available_strategies:
            print(f"[WARNING] Invalid strategy selected: {strategy}. Defaulting to SMA.")
            strategy = "sma"

        print(f"[INFO] Selected Strategy: {strategy}")

        granularity = os.getenv("GRANULARITY", "1hr")
        units = int(os.getenv("UNITS", "100000"))
        stop_profit = os.getenv("STOP_PROFIT", "0")
        stop_loss = os.getenv("STOP_LOSS", "0")

        # Convert stop values to float or None
        stop_profit = None if stop_profit == "n" else float(stop_profit)
        stop_loss = None if stop_loss == "n" else float(stop_loss)

        print(f"[INFO] Granularity: {granularity}, Units: {units}, Stop Profit: {stop_profit}, Stop Loss: {stop_loss}")

        # Example Trade Data (Replace with real trade data)
        trade_data = {
            "Strategy": strategy,
            "Granularity": granularity,
            "Units": units,
            "StopProfit": stop_profit,
            "StopLoss": stop_loss
        }

        # Write trade log to DynamoDB
        print(f"[INFO] Writing trade log for {instrument}...")
        write_trade_log(trade_id="T12345", currency_pair=instrument, trade_data=trade_data)

        print("[INFO] Lambda function execution completed successfully.")
        return {"status": "Success", "mode": mode, "instrument": instrument}

    except Exception as e:
        print(f"[ERROR] Lambda function failed: {str(e)}")
        return {"status": "Failed", "error": str(e)}
