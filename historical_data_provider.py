import requests
import pandas as pd
import time
import os

# Fetch historical data from changing to desired inputs from below
symbol = 'BTCUSDT'
interval = '1m'  
start_str = '02 Feb, 2023'
end_str = '13 Mar, 2023'

def fetch_binance_data(symbol, interval='1d', start_str='1 Jan, 2023', end_str='18 Jul, 2024'):
    base_url = 'https://api.binance.com/api/v3/klines'
    start_ts = int(pd.to_datetime(start_str).timestamp() * 1000)
    end_ts = int(pd.to_datetime(end_str).timestamp() * 1000)
    limit = 1000
    all_data = []

    while start_ts < end_ts:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_ts,
            'endTime': end_ts,
            'limit': limit
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        if not data:
            break
        all_data.extend(data)
        start_ts = data[-1][0] + 1  # move to the next timestamp
        time.sleep(1)  # to avoid hitting rate limits

    df = pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def save_to_csv(data, directory, symbol, interval, start_str, end_str):
    # Format the filename
    filename = f"{symbol}_{interval}_{start_str.replace(' ', '_')}_to_{end_str.replace(' ', '_')}.csv"
    filepath = os.path.join(directory, filename)
    
    # Rename columns to match Backtest expectations
    data.rename(columns={
        'timestamp': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    
    # Set 'Date' as the index
    data.set_index('Date', inplace=True)
    
    # Save to CSV
    data.to_csv(filepath)
    print(f"Data saved to {filepath}")

directory = r"C:\Users\Jesann\Documents\trading\history data file"

data = fetch_binance_data(symbol, interval, start_str, end_str)
save_to_csv(data, directory, symbol, interval, start_str, end_str)
