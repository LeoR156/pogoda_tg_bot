from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("Текущая погода"),
        KeyboardButton("Прогноз на 3 дня"),
        KeyboardButton("Прогноз на 5 дней"),
        KeyboardButton("Настройки")
    )
    return markup

def get_settings_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        KeyboardButton("Изменить город"),
        KeyboardButton("🔙 Назад в меню")
    )
    return markup

def get_cancel_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("Отмена"))
    return markup

def get_city_confirm_inline(city_name):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Да, сохранить", callback_data=f"save_city:{city_name}"),
        InlineKeyboardButton("Нет, отмена", callback_data="cancel_city")
    )
    return markup
