import os
import telebot
import requests

# 1. Забираем токены из переменных окружения (вспоминаем флаг -e в Docker!)
TG_TOKEN = os.getenv("TG_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Проверка, что переменные действительно переданы
if not TG_TOKEN or not WEATHER_API_KEY:
    print("ВНИМАНИЕ: Не заданы переменные окружения TG_TOKEN или WEATHER_API_KEY!")
    exit(1)

bot = telebot.TeleBot(TG_TOKEN)

# 2. Реакция на команду /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! 🌍 Напиши мне название любого города, и я пришлю прогноз погоды.")

# 3. Реакция на любой другой текст (названия городов)
@bot.message_handler(func=lambda message: True)
def get_weather(message):
    city = message.text.strip()
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    
    try:
        response = requests.get(url, params=params)
        
        # Если API вернуло код 200 (Всё Ок)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            
            # Формируем красивый ответ
            answer = f"🌡 Погода в городе {city.capitalize()}:\n"
            answer += f"Температура: {temp}°C\n"
            answer += f"На улице {desc}."
            
            bot.send_message(message.chat.id, answer)
            
        # Если API вернуло код 404 (Город не найден)
        elif response.status_code == 404:
            bot.send_message(message.chat.id, f"❌ Город '{city}' не найден. Проверь опечатку!")
            
        else:
            bot.send_message(message.chat.id, "⚠️ Ошибка связи с сервером погоды.")
            print(f"Ошибка API: Код {response.status_code}")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔌 Внутренняя ошибка бота.")
        print(f"Ошибка кода: {e}")

# Запуск постоянного опроса серверов Telegram
print("Бот запущен и ждет сообщений...")
bot.polling(none_stop=True)
