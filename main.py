import yfinance as yf
import talib as ta
import numpy as np
import telebot
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')
TICKERS = os.getenv('TICKERS')

# Telegram bot setup
bot = telebot.TeleBot(TELEGRAM_API_KEY, parse_mode=None)

class StockMonitor:
    def __init__(self, ticker, bb_period=20, rsi_period=14, upper_rsi=70, lower_rsi=30):
        self.ticker = ticker
        self.bb_period = bb_period
        self.rsi_period = rsi_period
        self.upper_rsi = upper_rsi
        self.lower_rsi = lower_rsi
    
    def fetch_ohlcv(self):
        data = yf.download(self.ticker, period='6mo', interval='1d')
        close_prices = data['Close'].values
        return close_prices
    
    def calculate_indicators(self, close_prices):
        # Bollinger Bands
        upper_band, middle_band, lower_band = ta.BBANDS(close_prices, timeperiod=self.bb_period)
        # RSI
        rsi = ta.RSI(close_prices, timeperiod=self.rsi_period)
        return upper_band, middle_band, lower_band, rsi
    
    def check_signals(self, close_prices, upper_band, lower_band, rsi):
        # Check for Buy and Sell signals
        last_close = close_prices[-1]
        last_lower_band = lower_band[-1]
        last_upper_band = upper_band[-1]
        last_rsi = rsi[-1]
        
        if last_close <= last_lower_band and last_rsi <= self.lower_rsi:
            return f"Buy signal for {self.ticker}: Price below lower Bollinger Band and RSI below threshold."
        elif last_close >= last_upper_band and last_rsi >= self.upper_rsi:
            return f"Sell signal for {self.ticker}: Price above upper Bollinger Band and RSI above threshold."
        else:
            return f"No signal for {self.ticker}."
    
    def monitor(self):
        close_prices = self.fetch_ohlcv()
        upper_band, middle_band, lower_band, rsi = self.calculate_indicators(close_prices)
        signal = self.check_signals(close_prices, upper_band, lower_band, rsi)
        # if "No signal" not in signal:
        self.send_telegram_message(signal)
        print(signal)
    
    def send_telegram_message(self, message):
        bot.send_message(CHAT_ID, message)

def getTickers():
  if not TICKERS:
    return []
  
  return TICKERS.split(',')

# Function to monitor a stock in a thread
def monitor_stock(ticker):
    stock_monitor = StockMonitor(ticker)
    while True:
        stock_monitor.monitor()
        time.sleep(60)  # Wait 1 minute before checking again

# Start monitoring each stock in a separate thread
if __name__ == "__main__":
    tickers = getTickers()
    print(f'Starting monitoring {len(tickers)} tickers: {tickers}')
    with ThreadPoolExecutor(max_workers=len(tickers)) as executor:
        for ticker in tickers:
            executor.submit(monitor_stock, ticker)
