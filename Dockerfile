# Используйте официальный образ Python как базовый
FROM python:3.12.2-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установите рабочую директорию в контейнере
WORKDIR /app
ENV BOT_TOKEN 7302072107:AAEPzNeEWG_WbWGpY13IZ7zIPpw7NxRWD74
# Копируйте файлы проекта в контейнер
COPY . /app

RUN pip install --upgrade pip
# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запустите бота
CMD ["python", "./main.py"]
