import pandas as pd
import requests
import time

def fetch_candles(symbol="ETHUSDT", interval="5m", limit=1000):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def find_support_levels(df, lookback=20, threshold=0.995):
    supports = []
    for i in range(lookback, len(df)):
        low_slice = df["low"][i - lookback:i]
        min_price = low_slice.min()
        if df["low"].iloc[i] <= min_price * threshold:
            supports.append((df["timestamp"].iloc[i], df["low"].iloc[i]))
    return supports

def check_signal(df):
    if len(df) < 21:
        print("No hay suficientes velas para análisis")
        return None, None

    support_levels = find_support_levels(df)
    last_close = df.iloc[-1]["close"]

    for time_support, price_support in reversed(support_levels):
        if abs(last_close - price_support) / price_support < 0.01:
            print(f"🟢 Señal de compra: Precio {last_close} cerca de soporte {price_support}")
            return last_close, price_support

    print("❌ No hay señal clara de compra")
    return None, None

def main():
    df = fetch_candles()
    signal, support = check_signal(df)
    if signal and support:
        with open("operaciones.csv", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{signal},{support}\n")
        print("✅ Señal registrada en operaciones.csv")

if __name__ == "__main__":
    main()
