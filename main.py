import requests
import time

# Константы
BOT_TOKEN = "8064631445:AAHtYaJltTv2uXcRmy9ciMf6sMENgbhHBc0"
CHAT_ID = "1119718895"
API_URL = "https://open-api.bingx.com/openApi/swap/v2/quote/contracts"
CHECK_INTERVAL = 30  # секунд
VOLUME_CHANGE_THRESHOLD = 2.0  # например, 2x рост

# Словарь для хранения предыдущих значений объёмов
previous_volumes = {}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Ошибка при отправке в Telegram: {response.text}")
    except Exception as e:
        print(f"Telegram ошибка: {e}")

def get_usdt_pairs():
    try:
        response = requests.get(API_URL)
        print(f"HTTP статус: {response.status_code}")
        print("Ответ от BingX (первые 500 символов):")
        print(response.text[:500])

        data = response.json()

        if 'data' not in data:
            print("Ключ 'data' не найден в ответе.")
            return []

        return [item for item in data['data'] if item['quoteAsset'] == "USDT"]
    except Exception as e:
        print(f"Ошибка при запросе пар: {e}")
        return []

def check_volumes():
    pairs = get_usdt_pairs()
    for pair in pairs:
        symbol = pair['symbol']
        volume = float(pair.get('volume24h', 0))

        if symbol in previous_volumes:
            prev_volume = previous_volumes[symbol]
            if prev_volume > 0:
                ratio = volume / prev_volume
                if ratio >= VOLUME_CHANGE_THRESHOLD:
                    message = f"📈 Объём {symbol} вырос в {ratio:.2f} раза!\nБыло: {prev_volume}, Стало: {volume}"
                    print(message)
                    send_telegram_message(message)
        previous_volumes[symbol] = volume

def main():
    print("👀 Запуск мониторинга объёмов на BingX...")
    while True:
        check_volumes()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()