# test_bot.py
from weather_utils import get_weather_comment


def test_weather_comment_hot():
    # Проверяем, что при +30 будет "Жара! ☀️"
    assert get_weather_comment(30) == "Жара! ☀️"


def test_weather_comment_cold():
    # Проверяем, что при -10 будет "Дубак! ❄️"
    assert get_weather_comment(-10) == "Дубак! ❄️"


def test_weather_comment_normal():
    # Проверяем промежуточное значение
    assert get_weather_comment(15) == "Нормальная погода ☁️"
