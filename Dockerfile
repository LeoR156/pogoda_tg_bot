FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Шаг 1: Копируем только файл с зависимостями
COPY requirements.txt .

# Шаг 2: Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Шаг 3: Копируем весь остальной код бота
COPY . .

# Указываем команду для запуска бота
CMD ["python", "tg.py"]
