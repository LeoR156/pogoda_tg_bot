import os
import telebot
import logging

import db
import keyboards as kb
import weather_api as wa

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация переменных окружения
TG_TOKEN = os.getenv("TG_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TG_TOKEN or not WEATHER_API_KEY:
    logger.error("Не заданы переменные окружения TG_TOKEN или WEATHER_API_KEY!")
    exit(1)

# Инициализация БД
db.init_db()

# Инициализация бота
bot = telebot.TeleBot(TG_TOKEN)

def get_user_city(user_id):
    user = db.get_user(user_id)
    if user and user['default_city']:
        return user['default_city']
    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Добавляем юзера в БД, если его еще нет
    db.add_user(user_id, username)
    
    welcome_text = (
        "Привет! 🌍 Я твой погодный бот.\n\n"
        "Я могу показывать текущую погоду и прогноз на несколько дней.\n"
        "Для удобства давай установим твой город по умолчанию."
    )
    
    user_city = get_user_city(user_id)
    if user_city:
        welcome_text += f"\n\nТвой текущий город: <b>{user_city}</b>"
        bot.send_message(message.chat.id, welcome_text, reply_markup=kb.get_main_menu(), parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, welcome_text, parse_mode="HTML")
        msg = bot.send_message(message.chat.id, "Напиши название города, который хочешь установить по умолчанию:", reply_markup=kb.get_cancel_menu())
        bot.register_next_step_handler(msg, process_city_input)

@bot.message_handler(commands=['stats'])
def admin_stats(message):
    if ADMIN_ID and str(message.from_user.id) == str(ADMIN_ID):
        count = db.get_users_count()
        bot.send_message(message.chat.id, f"📊 Уникальных пользователей в базе: {count}")
    else:
        # Игнорируем или выдаем сообщение о недостатке прав
        pass

@bot.message_handler(func=lambda message: message.text == "Настройки")
def settings_menu(message):
    user_city = get_user_city(message.from_user.id)
    text = "⚙️ Настройки\n"
    if user_city:
        text += f"Текущий город: <b>{user_city}</b>"
    else:
        text += "Город по умолчанию не установлен."
    bot.send_message(message.chat.id, text, reply_markup=kb.get_settings_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад в меню")
def back_to_main(message):
    bot.send_message(message.chat.id, "Возвращаемся в главное меню.", reply_markup=kb.get_main_menu())

@bot.message_handler(func=lambda message: message.text == "Изменить город")
def change_city_prompt(message):
    msg = bot.send_message(message.chat.id, "Напиши название нового города:", reply_markup=kb.get_cancel_menu())
    bot.register_next_step_handler(msg, process_city_input)

def process_city_input(message):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Действие отменено.", reply_markup=kb.get_main_menu())
        return
        
    city = message.text.strip()
    # Делаем проверочный запрос к API
    weather_data = wa.get_current_weather(city)
    
    if weather_data["success"]:
        real_city_name = weather_data["city"]
        text = (
            f"Город <b>{real_city_name}</b> найден!\n"
            f"Текущая температура: {weather_data['temp']}°C\n\n"
            f"Сохранить этот город как основной?"
        )
        bot.send_message(
            message.chat.id, 
            text, 
            reply_markup=kb.get_city_confirm_inline(real_city_name),
            parse_mode="HTML"
        )
    else:
        msg = bot.send_message(
            message.chat.id, 
            f"❌ {weather_data['error']}\nПопробуй ввести название еще раз или нажми 'Отмена'.",
            reply_markup=kb.get_cancel_menu()
        )
        bot.register_next_step_handler(msg, process_city_input)

@bot.callback_query_handler(func=lambda call: call.data.startswith('save_city:'))
def callback_save_city(call):
    city_name = call.data.split(':', 1)[1]
    user_id = call.from_user.id
    db.update_default_city(user_id, city_name)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Город <b>{city_name}</b> успешно сохранен!",
        parse_mode="HTML"
    )
    bot.send_message(call.message.chat.id, "Открываю главное меню:", reply_markup=kb.get_main_menu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_city')
def callback_cancel_city(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ Изменение города отменено."
    )
    bot.send_message(call.message.chat.id, "Возвращаемся в главное меню:", reply_markup=kb.get_main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text in ["Текущая погода", "Прогноз на 3 дня", "Прогноз на 5 дней"])
def weather_requests(message):
    user_city = get_user_city(message.from_user.id)
    
    if not user_city:
        msg = bot.send_message(message.chat.id, "Сначала укажите город. Напишите название:", reply_markup=kb.get_cancel_menu())
        bot.register_next_step_handler(msg, process_city_input)
        return
        
    bot.send_chat_action(message.chat.id, 'typing')
    
    if message.text == "Текущая погода":
        data = wa.get_current_weather(user_city)
        if data["success"]:
            answer = f"🌡 Погода в городе <b>{data['city']}</b>:\n"
            answer += f"Температура: <b>{data['temp']}°C</b>\n"
            answer += f"На улице: {data['desc']}."
            bot.send_message(message.chat.id, answer, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка: {data['error']}")
            
    elif message.text == "Прогноз на 3 дня" or message.text == "Прогноз на 5 дней":
        days = 3 if "3" in message.text else 5
        data = wa.get_forecast(user_city, days)
        if data["success"]:
            answer = f"📅 Прогноз погоды для <b>{data['city']}</b> на {days} дн.:\n\n"
            for day in data["forecast"]:
                answer += f"🔹 <b>{day['date']}</b>\n"
                answer += f"   Мин: {day['min_temp']}°C | Макс: {day['max_temp']}°C\n"
                answer += f"   {day['desc']}\n\n"
            bot.send_message(message.chat.id, answer, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка: {data['error']}")

@bot.message_handler(func=lambda message: True)
def unknown_text(message):
    # Если введен какой-то произвольный текст, предполагаем, что юзер хочет узнать погоду для этого города (разово)
    city = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')
    
    data = wa.get_current_weather(city)
    if data["success"]:
        answer = f"🌡 Текущая погода (разовый запрос) в <b>{data['city']}</b>:\n"
        answer += f"Температура: <b>{data['temp']}°C</b>\n"
        answer += f"На улице: {data['desc']}."
        bot.send_message(message.chat.id, answer, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, f"❌ {data['error']}\nИспользуйте меню или введите корректное название города.", reply_markup=kb.get_main_menu())

if __name__ == "__main__":
    logger.info("Бот запущен и ждет сообщений...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Критическая ошибка при поллинге: {e}")
