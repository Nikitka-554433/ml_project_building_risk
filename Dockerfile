# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копирование зависимостей и их установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего кода проекта
COPY . .

# порт для API
EXPOSE 8000

# Команда для запуска сервиса
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]