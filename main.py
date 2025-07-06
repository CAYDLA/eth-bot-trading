
import requests
import pandas as pd
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = '8088154821:AAH3pXp81Lotj6teAZ-Xz2IAsZksgUdep6g'
CHAT_ID = '6359194989'
CSV_FILE = 'trade_log.csv'

def fetch_data():
    url = 'https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=5m&limit=1000'
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['low'] = df['low'].astype(float)
    df['high'] = df['high'].astype(float)
    df['open'] = df['open'].astype(float)
    return df

def check_signal(df):
    last_close = df.iloc[-1]['close']
    support_zone = df['low'].rolling(20).min().iloc[-1]
    confirmation = df['close'].iloc[-1] > df['close'].iloc[-2]
    if last_close <= support_zone and confirmation:
        return True, support_zone
    return False, None

def log_trade(entry_price, take_profit, stop_loss):
    now = datetime.utcnow().isoformat()
    row = f"{now},{entry_price},{take_profit},{stop_loss}\n"
    with open(CSV_FILE, "a") as file:
        file.write(row)

def send_alert(message):
    Bot(token=TELEGRAM_TOKEN).send_message(chat_id=CHAT_ID, text=message)

def main():
    df = fetch_data()
    signal, support = check_signal(df)
    if signal:
        entry = df.iloc[-1]['close']
        sl = support - 5
        tp = entry + (entry - sl) * 1.5
        log_trade(entry, tp, sl)
        msg = f"📈 Señal de COMPRA detectada\nEntrada: {entry}\nTP: {tp:.2f}\nSL: {sl:.2f}"
        send_alert(msg)

if __name__ == "__main__":
    main()
