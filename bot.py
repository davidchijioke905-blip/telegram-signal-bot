import requests
import time
import pandas as pd
import numpy as np

# ====== TELEGRAM ======
BOT_TOKEN = "8562961472:AAGk9s4vSdF83EfXESQszR-jV2-NISYxS3c"
CHAT_ID = "6992574897"

# ====== ALPHA VANTAGE ======
API_KEY = "SI4E0RKF1YK2RRP8"
SYMBOL = "XAUUSD"
INTERVAL = "5min"

LOT_SIZE = 0.01  # safe for $12 balance

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data():
    url = (
        "https://www.alphavantage.co/query?"
        f"function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD"
        f"&interval={INTERVAL}&apikey={API_KEY}"
    )
    data = requests.get(url).json()
    prices = data[f"Time Series FX ({INTERVAL})"]
    df = pd.DataFrame(prices).T.astype(float)
    df.columns = ["open", "high", "low", "close"]
    return df[::-1]

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(period).mean() / loss.rolling(period).mean()
    return 100 - (100 / (1 + rs))

last_signal = None

while True:
    try:
        df = get_data()
        close = df["close"]

        ema20 = EMA(close, 20)
        ema50 = EMA(close, 50)
        rsi = RSI(close)

        price = close.iloc[-1]

        # BUY CONDITION
        if ema20.iloc[-1] > ema50.iloc[-1] and rsi.iloc[-1] > 55 and last_signal != "BUY":
            sl = round(price - 0.4, 2)
            tp = round(price + 0.8, 2)
            send(
                f"📈 BUY XAUUSD\n"
                f"Entry: {price}\n"
                f"SL: {sl}\n"
                f"TP: {tp}\n"
                f"Lot: {LOT_SIZE}"
            )
            last_signal = "BUY"

        # SELL CONDITION
        elif ema20.iloc[-1] < ema50.iloc[-1] and rsi.iloc[-1] < 45 and last_signal != "SELL":
            sl = round(price + 0.4, 2)
            tp = round(price - 0.8, 2)
            send(
                f"📉 SELL XAUUSD\n"
                f"Entry: {price}\n"
                f"SL: {sl}\n"
                f"TP: {tp}\n"
                f"Lot: {LOT_SIZE}"
            )
            last_signal = "SELL"

        # EXIT CONDITION
        elif last_signal and 45 < rsi.iloc[-1] < 55:
            send("⚠️ EXIT TRADE — Momentum weakening")
            last_signal = None

        time.sleep(300)

    except Exception:
        time.sleep(300)
