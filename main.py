import requests
import time
import os

BOT_TOKEN = "8064631445:AAHtYaJltTv2uXcRmy9ciMf6sMENgbhHBc0"
CHAT_ID = "1119718895"

VOLUME_MULTIPLIER = 2.5
CHECK_INTERVAL = 60  # секунд

API_URL = "https://open-api.bingx.com/openApi/swap/v2/quote/contracts"
HEADERS = {"User-Agent": "Mozilla/5.0"}

previous_volumes = {}

def get_usdt_pairs():
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if "data" not in data:
            print("Ключ 'data' не найден в ответе.")
            return []
        # Фильтруем пары с quoteAsset == USDT, в новом API — поле 'currency' == 'USDT'
        pairs = [item for item in data["data"] if item.get("currency") == "USDT"]
        print(f"Найдено пар с USDT: {len(pairs)}")
        return pairs
    except Exception as e:
        print("Ошибка при получении пар:", e)
        return []

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Ошибка при отправке в Telegram:", e)

def check_volume_spikes():
    pairs = get_usdt_pairs()
    for pair in pairs:
        symbol = pair["symbol"]
        volume = float(pair.get("volume24h", 0))
        prev_volume = previous_volumes.get(symbol, 0)

        if prev_volume > 0:
            ratio = volume / prev_volume
            if ratio >= VOLUME_MULTIPLIER:
                msg = (
                    f"🚨 *Объём всплеска!*\n"
                    f"Монета: `{symbol}`\n"
                    f"Объём (24ч): {volume:.2f}\n"
                    f"Предыдущий объём: {prev_volume:.2f}\n"
                    f"Рост в {ratio:.2f} раза!"
                )
                print(msg)
                send_telegram(msg)

        previous_volumes[symbol] = volume

def main():
    print("👀 Запуск мониторинга объёмов на BingX...")
    while True:
        check_volume_spikes()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()