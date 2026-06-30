import os
import requests
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"
TIMEOUT = 10

def get_current_weather(city: str) -> dict:
    url = f"{BASE_URL}/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "city": data["name"],
                "temp": data["main"]["temp"],
                "desc": data["weather"][0]["description"].capitalize()
            }
        elif response.status_code == 404:
            return {"success": False, "error": f"Город '{city}' не найден."}
        else:
            logger.error(f"API Error: Code {response.status_code} for city {city}")
            return {"success": False, "error": "Ошибка связи с сервером погоды."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
        return {"success": False, "error": "Превышено время ожидания или ошибка сети."}

def get_forecast(city: str, days: int) -> dict:
    url = f"{BASE_URL}/forecast"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            city_name = data["city"]["name"]
            
            # Агрегация данных по дням
            daily_data = defaultdict(lambda: {"temps": [], "descs": []})
            
            for item in data["list"]:
                # дата в формате 'YYYY-MM-DD HH:MM:SS'
                date_str = item["dt_txt"].split(" ")[0]
                daily_data[date_str]["temps"].append(item["main"]["temp"])
                daily_data[date_str]["descs"].append(item["weather"][0]["description"])
            
            # Сортируем дни
            sorted_dates = sorted(daily_data.keys())
            
            # Ограничиваем количество дней
            target_dates = sorted_dates[:days]
            
            result = []
            for date_str in target_dates:
                temps = daily_data[date_str]["temps"]
                descs = daily_data[date_str]["descs"]
                
                min_temp = min(temps)
                max_temp = max(temps)
                
                # Самое частое описание погоды за день
                most_common_desc = max(set(descs), key=descs.count).capitalize()
                
                # Перевод даты в читаемый формат
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d.%m.%Y")
                
                result.append({
                    "date": formatted_date,
                    "min_temp": min_temp,
                    "max_temp": max_temp,
                    "desc": most_common_desc
                })
                
            return {"success": True, "city": city_name, "forecast": result}
            
        elif response.status_code == 404:
            return {"success": False, "error": f"Город '{city}' не найден."}
        else:
            logger.error(f"API Error (Forecast): Code {response.status_code} for city {city}")
            return {"success": False, "error": "Ошибка связи с сервером погоды."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception (Forecast): {e}")
        return {"success": False, "error": "Превышено время ожидания или ошибка сети."}
