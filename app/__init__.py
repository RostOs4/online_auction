# Инициализация приложения
from flask import Flask

app = Flask(__name__)

# Импортируем маршруты
from app import routes

# Проверяем, запущено ли приложение напрямую
if __name__ == '__main__':
    app.run(debug=True)