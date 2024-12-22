# Используем официальный образ Python в качестве базового
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только необходимые файлы для установки зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Копируем остальные файлы приложения в контейнер
COPY . .

# Указываем переменную окружения для Flask
ENV FLASK_APP=app/app.py

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=8000"]