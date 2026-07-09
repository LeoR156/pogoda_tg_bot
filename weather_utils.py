def get_weather_comment(temperature):

    if temperature >= 25:
	return "Жара!"

    elif temperature <= 0:
	return "Дубак"

    else:
	return "Норма"
