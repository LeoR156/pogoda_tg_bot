# weather_utils.py


def get_weather_comment(temperature):
    """Возвращает текстовый комментарий и эмодзи в зависимости от температуры"""
    if temperature >= 25:
        return "Жара! ☀️"
    elif temperature <= 0:
        return "Дубак! ❄️"
    else:
        return "Нормальная погода ☁️"
