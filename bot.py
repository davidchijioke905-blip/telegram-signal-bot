import requests
import time

BOT_TOKEN = "8562961472:AAGk9s4vSdF83EfXESQszR-jV2-NISYxS3c
"
CHAT_ID = "6992574897"

def send_signal(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

while True:
    send_signal("📊 XAUUSD Signal Test: BUY @ Market\nSL: 20 pips\nTP: 40 pips")
    time.sleep(3600)
