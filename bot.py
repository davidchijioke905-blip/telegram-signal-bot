import requests
import json
import logging
import time
import telebot
import numpy as np

# Config
API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"
SYMBOL = "XAUUSD"
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
LOT_SIZE = 0.01

bot = telebot.TeleBot(BOT_TOKEN)

# Store current positions
positions = {}

def get_live_data():
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=XAU&to_currency=USD&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])

def strategy(price, prices):
    # Simple moving average crossover strategy
    short_window = 5
    long_window = 10
    if len(prices) < long_window:
        return None
    short_ma = np.mean(prices[-short_window:])
    long_ma = np.mean(prices[-long_window:])
    if short_ma > long_ma:
        return "BUY"
    elif short_ma < long_ma:
        return "SELL"
    return None

def send_signal(message):
    bot.send_message(CHAT_ID, message)

def manage_position(price):
    if CHAT_ID in positions:
        entry_price = positions[CHAT_ID]["entry_price"]
        direction = positions[CHAT_ID]["direction"]
        profit = (price - entry_price) * LOT_SIZE * (1 if direction == "BUY" else -1)
        if profit >= 1:
            send_signal(f"CLOSE {direction} XAUUSD @ {price:.2f}, Profit: ${profit:.2f}")
            del positions[CHAT_ID]
            return
    prices = positions.get(CHAT_ID, {}).get("prices", [])
    prices.append(price)
    signal = strategy(price, prices)
    if signal:
        if CHAT_ID not in positions:
            entry_price = price
            positions[CHAT_ID] = {"entry_price": entry_price, "direction": signal, "prices": prices}
            tp = entry_price * (1.005 if signal == "BUY" else 0.995)
            sl = entry_price * (0.995 if signal == "BUY" else 1.005)
            send_signal(f"{signal} XAUUSD @ {entry_price:.2f}, TP {tp:.2f}, SL {sl:.2f}")
        elif positions[CHAT_ID]["direction"] != signal:
            # Close current position and open new one
            entry_price = positions[CHAT_ID]["entry_price"]
            direction = positions[CHAT_ID]["direction"]
            profit = (price - entry_price) * LOT_SIZE * (1 if direction == "BUY" else -1)
            send_signal(f"CLOSE {direction} XAUUSD @ {price:.2f}, Profit: ${profit:.2f}")
            entry_price = price
            positions[CHAT_ID] = {"entry_price": entry_price, "direction": signal, "prices": prices}
            tp = entry_price * (1.005 if signal == "BUY" else 0.995)
            sl = entry_price * (0.995 if signal == "BUY" else 1.005)
            send_signal(f"{signal} XAUUSD @ {entry_price:.2f}, TP {tp:.2f}, SL {sl:.2f}")

while True:
    try:
        price = get_live_data()
        manage_position(price)
        time.sleep(60)  # Check every 60 seconds
    except Exception as e:
        logging.error(f"Error: {e}")
