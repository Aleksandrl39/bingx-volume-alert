import requests
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

VOLUME_MULTIPLIER = 2.5
CHECK_INTERVAL = 60  # секунд

PAIRS_URL = "https://api.bingx.com/api/v1/market/symbols"
CANDLES_URL = "https://api.bingx.com/api/v1/market/candles"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_usdt_pairs():
    url = "https://open-api.bingx.com/openApi/swap/v2/market/getAllContracts"
    response = requests.get(url)
    print("Ответ от BingX:")
    print(response.text)  # <-- добавлено
    data = response.json()
    return [item['symbol'] for item in data['data'] if item['quoteAsset'] == "USDT"]

def get_candle_volume(symbol, limit=20):
    params = {"symbol": symbol, "interval": "1m", "limit": limit}
    res = requests.get(CANDLES_URL, params=params, headers=HEADERS)
    res.raise_for_status()
    return [float(candle[5]) for candle in res.json()['data']]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except:
        pass

def main():
    print("👀 Запуск мониторинга объёмов на BingX...")
    pairs = get_usdt_pairs()
    print(f"✅ Найдено {len(pairs)} пар USDT")

    while True:
        for symbol in pairs:
            try:
                volumes = get_candle_volume(symbol)
                if len(volumes) < 10:
                    continue
                avg_vol = sum(volumes[:-1]) / (len(volumes) - 1)
                last_vol = volumes[-1]

                if last_vol > avg_vol * VOLUME_MULTIPLIER:
                    text = (
                        f"🚨 *Объём всплеска!*\n"
                        f"Монета: `{symbol}`\n"
                        f"Объём (1 мин): {last_vol:.2f}\n"
                        f"Средний объём: {avg_vol:.2f}"
                    )
                    send_telegram(text)
            except Exception as e:
                print(f"Ошибка по {symbol}: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
