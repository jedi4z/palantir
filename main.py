from dotenv import load_dotenv
import os
import talib as ta
import telebot
import time
import yfinance as yf

load_dotenv()

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')
TICKERS = os.getenv('TICKERS')

# Telegram bot setup
bot = telebot.TeleBot(TELEGRAM_API_KEY, parse_mode=None)

class StockMonitor:
    def __init__(self, ticker, bb_period=20, rsi_period=21, ma_period=200, upper=67, lower=43):
        self.ticker = ticker
        self.bb_period = bb_period
        self.rsi_period = rsi_period
        self.ma_period = ma_period
        self.upper = upper
        self.lower = lower
    
    def fetch_ohlcv(self):
        print(f'fetching data for {self.ticker}')
        data = yf.download(self.ticker, period='6mo', interval='1d')
        close_prices = data['Close'].values
        high_prices = data['High'].values
        low_prices = data['Low'].values
        return close_prices, high_prices, low_prices
    
    def calculate_indicators(self, close_prices):
        bb_upper_band, _, bb_lower_band = ta.BBANDS(close_prices, timeperiod=self.bb_period)
        rsi = ta.RSI(close_prices, timeperiod=self.rsi_period)
        ma = ta.MA(close_prices, timeperiod=self.ma_period)
        return bb_upper_band, bb_lower_band, rsi, ma
    
    def check_signals(self, close_prices, high_prices, low_prices, bb_upper_band, bb_lower_band, rsi, ma):
        last_high = high_prices[-1]
        last_low = low_prices[-1]
        last_bb_upper = bb_upper_band[-1]
        last_bb_lower = bb_lower_band[-1]
        last_rsi = rsi[-1]
        last_ma = ma[-1]

        if (last_low <= last_bb_lower) and (last_rsi <= self.lower):
            return (
                f"<b>Buy Signal for {self.ticker}:</b>\n"
                f"<i>Lower Price</i>: {last_low:.2f}\n"
                f"<i>Lower Bollinger Band</i>: {last_bb_lower:.2f}\n"
                f"<i>RSI</i>: {last_rsi:.2f}\n"
                f"<i>Condition</i>: Price below lower Bollinger Band and RSI below threshold.\n"
                f"🔥🔥🔥🔥🔥🔥"
            )
        elif (last_high >= last_bb_upper) \
          and (last_high > last_ma) \
          and (last_rsi >= self.upper):
            return (
                f"<b>Sell Signal for {self.ticker}:</b>\n"
                f"<i>Highest Price</i>: {last_high:.2f}\n"
                f"<i>Upper Bollinger Band</i>: {last_bb_upper:.2f}\n"
                f"<i>RSI</i>: {last_rsi:.2f}\n"
                f"<i>Condition</i>: Price above upper Bollinger Band and RSI above threshold.\n"
                f"💎💎💎💎💎💎"
            )
        else:
            return f"<i>No signal for {self.ticker}.</i>"
    
    def monitor(self):
        close_prices, high_prices, low_prices = self.fetch_ohlcv()
        bb_upper_band, bb_lower_band, rsi, ma = self.calculate_indicators(close_prices)
        signal = self.check_signals(close_prices, high_prices, low_prices, bb_upper_band, bb_lower_band, rsi, ma)
        if "No signal" not in signal:
            self.send_telegram_message(signal)
        print(signal)
    
    def send_telegram_message(self, message):
        bot.send_message(CHAT_ID, message, parse_mode='HTML')

def getTickers():
  if not TICKERS:
    return []
  return TICKERS.split(',')


if __name__ == "__main__":
    tickers = getTickers()
    print(f'Starting monitoring {len(tickers)} tickers: {tickers}')

    while True:
        for ticker in tickers:
            stock_monitor = StockMonitor(ticker)
            stock_monitor.monitor()
        time.sleep(60)
