import streamlit as st
import requests
import pandas as pd
import time
import os

# Function to fetch historical data from Binance
def fetch_binance_data(symbol, interval='1d', start_str='1 Jan, 2023', end_str='18 Jul, 2024'):
    base_url = 'https://api.binance.com/api/v3/klines'  # Binance API endpoint
    start_ts = int(pd.to_datetime(start_str).timestamp() * 1000)  # Convert start date to milliseconds
    end_ts = int(pd.to_datetime(end_str).timestamp() * 1000)  # Convert end date to milliseconds
    limit = 1000  # Maximum number of records to fetch in one request
    all_data = []  # List to hold all fetched data

    # Loop to keep fetching data until we reach the end date
    while start_ts < end_ts:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_ts,
            'endTime': end_ts,
            'limit': limit
        }
        response = requests.get(base_url, params=params)  # Make the API request
        data = response.json()  # Convert response to JSON
        if not data:
            break  # Exit loop if no more data is returned
        all_data.extend(data)  # Append new data to the list
        start_ts = data[-1][0] + 1  # Move to the next timestamp for the next request
        time.sleep(1)  # Pause briefly to avoid hitting API rate limits

    # Create a DataFrame from the collected data
    df = pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Convert timestamp to datetime
    return df  

# Function to save the data to a CSV file
def save_to_csv(data, filename):
    # Rename columns to match the format expected for backtesting
    data.rename(columns={
        'timestamp': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    
    # Set 'Date' as the index for better data handling
    data.set_index('Date', inplace=True)
    
    # Convert DataFrame to CSV and provide a download option in Streamlit
    csv = data.to_csv().encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=filename,
        mime='text/csv',
    )

# Streamlit interface function
def main():
    st.title('Binance Historical Data Fetcher')  # Title of the app

    # User input for the cryptocurrency symbol
    symbol = st.text_input('Symbol', value='BTCUSDT')
    # User selection for the time interval
    interval = st.selectbox('Interval', options=['1m', '5m', '15m', '30m', '1h', '4h', '1d'], index=0)
    
    # Date input widgets for start and end dates
    st.write("### Select Start Date")
    start_date = st.date_input('Start Date', pd.to_datetime('2023-02-02'))
    
    st.write("### Select End Date")
    end_date = st.date_input('End Date', pd.to_datetime('2023-03-13'))

    # Convert selected dates to string format for the API request
    start_str = start_date.strftime('%d %b, %Y')
    end_str = end_date.strftime('%d %b, %Y')

    # Button to initiate the data fetch
    if st.button('Fetch Data'):
        with st.spinner('Fetching data...'):  # Show a loading spinner
            data = fetch_binance_data(symbol, interval, start_str, end_str)  # Fetch the data
            st.success('Data fetched successfully!')  # Notify user of success

            # Display the first few rows of the fetched data
            st.write(data.head())

            # Create a filename suggestion for the downloaded CSV
            filename = f"{symbol}_{interval}_{start_str.replace(' ', '_')}_to_{end_str.replace(' ', '_')}.csv"
            
            # Provide the option to save the data to a CSV file
            save_to_csv(data, filename)

# Run the app
if __name__ == "__main__":
    main()
